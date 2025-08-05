import os
import shutil
import sys

import click

from biolib import utils  # Import like this to let BASE_URL_IS_PUBLIC_BIOLIB be set correctly
from biolib._internal.add_copilot_prompts import add_copilot_prompts
from biolib._internal.add_gui_files import add_gui_files
from biolib._internal.string_utils import normalize_for_docker_tag
from biolib._internal.templates import templates
from biolib.utils import BIOLIB_PACKAGE_VERSION


@click.command(help='Initialize a BioLib project', hidden=True)
def init() -> None:
    cwd = os.getcwd()

    app_uri = input('What URI do you want to create the application under? (leave blank to skip): ')
    app_name = app_uri.split('/')[-1] if app_uri else None
    docker_tag = normalize_for_docker_tag(app_name) if app_name else None
    if not app_uri:
        print(
            'Remember to set the app URI in the .biolib/config.yml file later, '
            'and docker image name in the .biolib/config.yml and .github/workflows/biolib.yml files.'
        )
    advanced_setup_input = input('Do you want to set up advanced features like Copilot and GUI? [y/N]: ')
    advanced_setup = advanced_setup_input.lower() == 'y'
    include_copilot = False
    include_gui = False
    if advanced_setup:
        copilot_enabled_input = input('Do you want to include Copilot instructions and prompts? [y/N]: ')
        include_copilot = copilot_enabled_input.lower() == 'y'
        include_gui_input = input('Do you want to include GUI setup? [y/N]: ')
        include_gui = include_gui_input.lower() == 'y'

    init_template_dir = templates.init_template()
    conflicting_files = []
    files_to_overwrite = set()

    try:
        # First pass: check for conflicts
        for root, dirs, filenames in os.walk(init_template_dir):
            dirs[:] = [d for d in dirs if '__pycache__' not in d]
            relative_dir = os.path.relpath(root, init_template_dir)
            destination_dir = cwd if relative_dir == '.' else os.path.join(cwd, relative_dir)

            for filename in filenames:
                source_file = os.path.join(root, filename)
                destination_file = os.path.join(destination_dir, filename)
                if os.path.exists(destination_file):
                    with open(source_file, 'rb') as fsrc, open(destination_file, 'rb') as fdest:
                        if fsrc.read() != fdest.read():
                            conflicting_files.append(os.path.relpath(destination_file, cwd))

        if conflicting_files:
            print('The following files already exist and would be overwritten:')
            for conflicting_file in conflicting_files:
                print(f'  {conflicting_file}')
            print()

            for conflicting_file in conflicting_files:
                choice = input(f'Overwrite {conflicting_file}? [y/N]: ').lower().strip()
                if choice in ['y', 'yes']:
                    files_to_overwrite.add(conflicting_file)

        replace_app_uri = app_uri if app_uri else 'PUT_APP_URI_HERE'
        replace_app_name = app_name if app_name else 'biolib-app'

        # Second pass: copy files (only if no conflicts)
        for root, dirs, filenames in os.walk(init_template_dir):
            dirs[:] = [d for d in dirs if '__pycache__' not in d]
            relative_dir = os.path.relpath(root, init_template_dir)
            destination_dir = os.path.join(cwd, relative_dir)

            os.makedirs(destination_dir, exist_ok=True)

            for filename in filenames:
                if utils.BASE_URL_IS_PUBLIC_BIOLIB and filename == 'biolib.yml':
                    continue

                relative_file_path = os.path.join(relative_dir, filename) if relative_dir != '.' else filename

                source_file = os.path.join(root, filename)
                destination_file = os.path.join(destination_dir, filename)
                relative_file_path = os.path.relpath(destination_file, cwd)

                if not os.path.exists(destination_file) or relative_file_path in files_to_overwrite:
                    try:
                        with open(source_file) as f:
                            content = f.read()

                        new_content = content.replace('BIOLIB_REPLACE_PYBIOLIB_VERSION', BIOLIB_PACKAGE_VERSION)
                        new_content = new_content.replace('BIOLIB_REPLACE_APP_URI', replace_app_uri)
                        new_content = new_content.replace(
                            'BIOLIB_REPLACE_DOCKER_TAG',
                            docker_tag if docker_tag else 'PUT_DOCKER_TAG_HERE',
                        )
                        new_content = new_content.replace('BIOLIB_REPLACE_APP_NAME', replace_app_name)

                        gui_config = "main_output_file: '/result.html'\n" if include_gui else ''
                        new_content = new_content.replace('BIOLIB_REPLACE_GUI_CONFIG\n', gui_config)

                        gui_mv_command = 'mv result.html output/result.html\n' if include_gui else ''
                        new_content = new_content.replace('BIOLIB_REPLACE_GUI_MV_COMMAND\n', gui_mv_command)

                        with open(destination_file, 'w') as f:
                            f.write(new_content)
                    except UnicodeDecodeError:
                        shutil.copy2(source_file, destination_file)

        readme_path = os.path.join(cwd, 'README.md')
        if not os.path.exists(readme_path) and app_name:
            with open(readme_path, 'w') as readme_file:
                readme_file.write(f'# {app_name}\n')

        if include_copilot:
            add_copilot_prompts(force=False, silent=True)

        if include_gui:
            add_gui_files(force=False, silent=True)

    except KeyboardInterrupt:
        print('\nInit command cancelled.', file=sys.stderr)
        exit(1)
