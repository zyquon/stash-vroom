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

# Entry point for the Stash plugin.
# This just preprares the venv and the execs that for the real work.

import os
import sys
import venv
import json

import stash_log as log

log.info('Start')
json_input_str = sys.stdin.read()
json_input = json.loads(json_input_str)

plugin_dir = json_input['server_connection']['PluginDir']
venv_dir = f'{plugin_dir}/venv-stash'
python_executable = f'{venv_dir}/bin/python'
deps_py = f'{plugin_dir}/stash-plugin/deps.py'

if not os.path.exists(venv_dir):
    log.info(f'Create virtual environment: {venv_dir}')
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(venv_dir)

log.info(f'Execute step 2: Dependencies')
os.environ['STASH_INPUT'] = json_input_str
os.execv(python_executable, [python_executable, deps_py])