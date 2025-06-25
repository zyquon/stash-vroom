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

# Daemon for the Stash plugin.

import os
import sys
import json
import logging
from logging.handlers import RotatingFileHandler

import stash_log

log_file = '/tmp/stash_plugin.log'
handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log = logging.getLogger('stash-plugin')
log.setLevel(logging.DEBUG)
log.addHandler(handler)

log.info('Stash plugin: start daemon')
json_input_str = os.environ.get('STASH_INPUT')
if not json_input_str:
    log.error('Exit: STASH_INPUT environment variable not set')
    stash_log.error('Exit: STASH_INPUT environment variable not set')
    sys.exit(1)

json_input = json.loads(json_input_str)
log.info(f'Yay, got input:\n{json.dumps(json_input, indent=2)}')

# Now just sleep for 30 seconds.
import time
delay = 60 * 0.5
log.info(f'Sleep: {delay} seconds')
time.sleep(delay)
log.info(f'Done sleeping: {delay} seconds')