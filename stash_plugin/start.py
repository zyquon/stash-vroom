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

# Entry point for the Stash plugin.
# This just preprares the venv with the dependencies and the execs that for the real work.

import os
import sys
import venv
import json
import logging
import subprocess
import logging.handlers

import stash_log as log

# log_file = '/tmp/stash_plugin.log'
# handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
# handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
# log = logging.getLogger('stash_plugin')
# log.setLevel(logging.DEBUG)
# log.addHandler(handler)

log.info('Stash-VRoom: Start')
json_input_str = sys.stdin.read()
json_input = json.loads(json_input_str)

plugin_dir = json_input['server_connection']['PluginDir']
venv_dir = f'{plugin_dir}/.stash-venv'
pip_executable = f'{venv_dir}/bin/pip'
python_executable = f'{venv_dir}/bin/python'
continue_py = f'{plugin_dir}/stash_plugin/continue.py'

if not os.path.exists(venv_dir):
    log.info(f'Create virtual environment: {venv_dir}')
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(venv_dir)

    # TODO: As soon as the dependencies or versons change, this will need to do something smarter.
    # Maybe this only sets the venv, then it execs that python to run an intermediate pip.py
    # which specifically confirms or upgrades the dependencies. Then pip.py execs the final continue.py.
    log.info(f'Install dependencies: {venv_dir}')
    try:
        subprocess.check_call([pip_executable, 'install', '-e', plugin_dir])
    except subprocess.CalledProcessError as e:
        log.error(f'Failed to install dependencies: {e}')
        sys.exit(1)
    else:
        log.debug('Dependencies installed successfully')

# log.info(f'Execute: {python_executable}')
os.execv(python_executable, [python_executable, continue_py, json_input_str])