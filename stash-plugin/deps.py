# Copyright 2024 Zyquo Onrel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Second execution step for the Stash plugin.
# This is running in the correct Python venv. It confirm as fast as possible that
# all dependencies are installed and then to executes daemon.py.

import os
import sys
import json
import subprocess

import stash_log as log

log.info('Stash-VRoom step 2: Dependencies')
json_input_str = os.environ.get('STASH_INPUT')
if not json_input_str:
    log.error('Exit: STASH_INPUT environment variable not set')
    sys.exit(1)

json_input = json.loads(json_input_str)
plugin_dir = json_input['server_connection']['PluginDir']
venv_dir = f'{plugin_dir}/venv-stash'
server_py = f'{plugin_dir}/stash-plugin/hs_server.py'

if os.environ.get(f'SKIP_VROOM_INSTALL'):
    # TODO: This could be a setting in the UI.
    log.debug(f'Skip dependency install')
else:
    # log.info(f'Install dependencies: {venv_dir}')
    try:
        result = subprocess.run(
            [f'{venv_dir}/bin/pip', 'install', '-e', plugin_dir],
            capture_output=True,
            text=True
        )
        result.check_returncode()  # Raise CalledProcessError if return code is non-zero
    except subprocess.CalledProcessError as e:
        log.error(f'Failed to install dependencies: {e}')
        sys.exit(1)
    finally:
        # log.info(f'Pip install stdout: {result.stdout!r}')
        if result and result.stderr:
            log.error(f'Pip install error message: {result.stderr}')

log.info(f'Start HereSphere server in the background')
background_process = subprocess.Popen(
    [f'{venv_dir}/bin/python', server_py],
    # stdout=subprocess.DEVNULL,  # Redirect stdout to avoid clutter
    stdout=sys.stdout,           # Redirect stdout to the parent process
    # stderr=subprocess.DEVNULL,  # Redirect stderr to avoid clutter
    stderr=sys.stderr,           # Redirect stderr to the parent process
    # start_new_session=True,     # Detach the process from the parent
    start_new_session=False,    # Keep the process in the same session
    env=os.environ,             # Pass the updated environment
)

log.info(f'Started HereSphere server in the background: PID {background_process.pid}')
sys.exit(0)