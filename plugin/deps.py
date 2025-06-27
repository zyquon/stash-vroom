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

import util
import stash_log

stash_log.debug('VRoom step 2: Dependencies')

json_input = util.get_stash_input()
plugin_dir = json_input['server_connection']['PluginDir']
venv_dir = f'{plugin_dir}/venv-stash'
runner_py = f'{plugin_dir}/plugin/runner.py'

# Attempt to ascertain if the plugin setting `skipDependencyCheck` is true. If so, skip. If anything goes wrong, proceed with the dependency check.
skip_check = False
try:
    import stash_vroom.stash
    stash_url = util.get_stash_input_url()
    stash_headers = util.get_stash_input_headers()
    client = stash_vroom.stash.init(stash_url, stash_headers)
    response = client.configuration().model_dump()
    my_config = response['configuration']['plugins'].get('VRoom', {})
    skip_check = my_config.get('skipDependencyCheck', False)
except Exception as e:
    stash_log.warning(f'Proceeding with dependency check due to error: {e}')

if skip_check:
    stash_log.debug(f'Skip dependency check and upgrade')
else:
    # stash_log.info(f'Install dependencies: {venv_dir}')
    try:
        result = subprocess.run(
            [f'{venv_dir}/bin/pip', 'install', '-e', plugin_dir],
            capture_output=True,
            text=True
        )
        result.check_returncode()  # Raise CalledProcessError if return code is non-zero
    except subprocess.CalledProcessError as e:
        stash_log.error(f'Failed to install dependencies: {e}')
        sys.exit(1)
    finally:
        # stash_log.info(f'Pip install stdout: {result.stdout!r}')
        if result and result.stderr:
            stash_log.error(f'Pip install error message: {result.stderr}')

stash_log.debug(f'Start HereSphere runner in the background')
background_process = subprocess.Popen(
    [f'{venv_dir}/bin/python', runner_py],
    # stdout=subprocess.DEVNULL,  # Redirect stdout to avoid clutter
    stdout=sys.stdout,           # Redirect stdout to the parent process
    # stderr=subprocess.DEVNULL,  # Redirect stderr to avoid clutter
    stderr=sys.stderr,           # Redirect stderr to the parent process
    # start_new_session=True,     # Detach the process from the parent
    start_new_session=False,    # Keep the process in the same session
    env=os.environ,             # Pass the updated environment
)

# stash_log.debug(f'Started HereSphere runner in the background: PID {background_process.pid}')
sys.exit(0)