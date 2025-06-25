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

import sys
import json
import logging
from logging.handlers import RotatingFileHandler
from venv import EnvBuilder

import stash_log

# Setup logging
log_file = '/tmp/stash_plugin.log'
handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log = logging.getLogger('stash-plugin')
log.setLevel(logging.DEBUG)
log.addHandler(handler)

log.info('Stash plugin: continue')
if len(sys.argv) < 2:
    log.error('No JSON input provided. Exiting.')
    stash_log.error('No JSON input provided. Exiting.')
    sys.exit(1)

try:
    json_input = json.loads(sys.argv[1])
except (json.JSONDecodeError, TypeError) as e:
    log.error(f'Failed to parse JSON input: {e}')
    stash_log.error(f'Failed to parse JSON input: {e}')
    sys.exit(1)

log.info(f'Yay, got input:\n{json.dumps(json_input, indent=2)}')

# Now just sleep for 30 seconds.
import time
log.info('Sleeping for 30 seconds...')
time.sleep(30)