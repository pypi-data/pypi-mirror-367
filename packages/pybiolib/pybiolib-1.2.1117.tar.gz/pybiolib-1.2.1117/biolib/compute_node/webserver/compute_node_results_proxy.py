import io
import tarfile
import time

from docker.models.containers import Container

from biolib.biolib_docker_client import BiolibDockerClient
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger_no_user_data
from biolib.compute_node.utils import BIOLIB_PROXY_NETWORK_NAME
from biolib.typing_utils import Optional
from biolib.compute_node.webserver.proxy_utils import get_biolib_nginx_proxy_image

class ComputeNodeResultsProxy:
    _instance: Optional['ComputeNodeResultsProxy'] = None

    def __init__(self, tls_pem_certificate_path: str, tls_pem_key_path: str):
        assert tls_pem_certificate_path, "tls_pem_certificate_path is required"
        assert tls_pem_key_path, "tls_pem_key_path is required"
        self._name = 'biolib-compute-node-results-proxy'
        self._container: Optional[Container] = None
        self._docker = BiolibDockerClient().get_docker_client()
        self._tls_pem_certificate_path = tls_pem_certificate_path
        self._tls_pem_key_path = tls_pem_key_path

    @staticmethod
    def start_proxy(tls_pem_certificate_path: str, tls_pem_key_path: str) -> None:
        if ComputeNodeResultsProxy._instance is None:
            ComputeNodeResultsProxy._instance = ComputeNodeResultsProxy(tls_pem_certificate_path, tls_pem_key_path)
            ComputeNodeResultsProxy._instance._start()  # pylint: disable=protected-access

    @staticmethod
    def stop_proxy() -> None:
        if ComputeNodeResultsProxy._instance is not None:
            ComputeNodeResultsProxy._instance._terminate()  # pylint: disable=protected-access
            ComputeNodeResultsProxy._instance = None

    def _start(self) -> None:
        docker = BiolibDockerClient.get_docker_client()

        for index in range(3):
            logger_no_user_data.debug(
                f'Attempt {index} at creating ComputeNodeResultsProxy container "{self._name}"...'
            )
            try:
                self._container = docker.containers.create(
                    detach=True,
                    image=get_biolib_nginx_proxy_image(),
                    name=self._name,
                    network=BIOLIB_PROXY_NETWORK_NAME,
                    ports={'443/tcp': 20443},
                    volumes={
                        self._tls_pem_certificate_path: {'bind': '/etc/ssl/certs/certificate.pem', 'mode': 'ro'},
                        self._tls_pem_key_path: {'bind': '/etc/ssl/private/private_key.pem', 'mode': 'ro'},
                    },
                )
                break
            except Exception as error:
                logger_no_user_data.exception(f'Failed to create container "{self._name}" hit error: {error}')

            logger_no_user_data.debug('Sleeping before re-trying container creation...')
            time.sleep(3)

        if not self._container or not self._container.id:
            raise BioLibError(f'Exceeded re-try limit for creating container {self._name}')

        self._write_nginx_config_to_container()
        self._container.start()

        proxy_is_ready = False
        for retry_count in range(1, 5):
            time.sleep(0.5 * retry_count)
            container_logs = self._container.logs()
            if b'ready for start up\n' in container_logs or b'start worker process ' in container_logs:
                proxy_is_ready = True
                break

        if not proxy_is_ready:
            self._terminate()
            raise Exception('ComputeNodeResultsProxy did not start properly')

        self._container.reload()

    def _terminate(self):
        if self._container:
            self._container.remove(force=True)


    def _write_nginx_config_to_container(self) -> None:
        if not self._container:
            raise Exception('ComputeNodeResultsProxy container not defined when attempting to write NGINX config')

        docker = BiolibDockerClient.get_docker_client()

        nginx_config = """
events {
  worker_connections  1024;
}

http {
    client_max_body_size 0;
    resolver 127.0.0.11 ipv6=off valid=30s;

    server {
        listen       443 ssl;
        ssl_certificate /etc/ssl/certs/certificate.pem;
        ssl_certificate_key /etc/ssl/private/private_key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
        ssl_prefer_server_ciphers on;

        location / {
            if ($http_biolib_result_uuid = "") {
                return 400 "Missing biolib-result-uuid header";
            }

            if ($http_biolib_result_port = "") {
                return 400 "Missing biolib-result-port header";
            }

            set $target_host "biolib-app-caller-proxy-$http_biolib_result_uuid";
            proxy_pass http://$target_host:1080;
            proxy_set_header biolib-result-uuid $http_biolib_result_uuid;
            proxy_set_header biolib-result-port $http_biolib_result_port;
            proxy_pass_request_headers on;
        }
    }
}
"""

        nginx_config_bytes = nginx_config.encode()
        tarfile_in_memory = io.BytesIO()
        with tarfile.open(fileobj=tarfile_in_memory, mode='w:gz') as tar:
            info = tarfile.TarInfo('/nginx.conf')
            info.size = len(nginx_config_bytes)
            tar.addfile(info, io.BytesIO(nginx_config_bytes))

        tarfile_bytes = tarfile_in_memory.getvalue()
        tarfile_in_memory.close()
        docker.api.put_archive(self._container.id, '/etc/nginx', tarfile_bytes)
