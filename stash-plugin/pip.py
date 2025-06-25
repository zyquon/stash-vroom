# Copyright 2023 Zyquo Onrel
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
# This is running in the correct Python venv so its job is to confirm as fast as possible that
# all dependencies are installed and then to execute the continue.py script.

import os
import sys
import json
import subprocess

import stash_log as log

log.info('Stash-VRoom: Pip')
if len(sys.argv) < 2:
    log.error('Exit: No JSON input provided')
    sys.exit(1)

json_input_str = sys.argv[1]
json_input = json.loads(json_input_str)

plugin_dir = json_input['server_connection']['PluginDir']
venv_dir = f'{plugin_dir}/venv-stash'
continue_py = f'{plugin_dir}/stash-plugin/continue.py'

# TODO: Possibly this could specifically check each package required but I'm not sure
# if that's practically faster than a `pip install` where everything is already installed.
log.info(f'Install dependencies: {venv_dir}')
try:
    subprocess.check_call([f'{venv_dir}/bin/pip', 'install', '-e', plugin_dir])
except subprocess.CalledProcessError as e:
    log.error(f'Failed to install dependencies: {e}')
    sys.exit(1)

log.info(f'Execute: {continue_py}')
os.execv(f'{venv_dir}/bin/python', [f'{venv_dir}/bin/python', continue_py, json_input_str])