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

# HereSphere server as a Stash plugin.

import os
import sys
import json
import stash_log

stash_log.debug(f'Load')

import logging
import logging.handlers
# from logging.handlers import RotatingFileHandler

try:
    from stash_vroom.heresphere import HereSphere
except ImportError as e:
    stash_log.error(f'Failed to load Stash-VRoom Python package: {e}')
    raise

log = None

# TODO: Just defining this object causes a query to Stash via API.
# I think that could be postponed to the .run() method. That way you could define everything
# and then figure out your API key and pass that to the run method. The way it is now, you have to
# have the API key ready and pass it to the constructor
app = HereSphere('Stash-VRoom')

# @app.on_eoubleclick()
# def on_doubleclick(scene_id, start_ts):
#     log.info(f"Double-click scene at {start_ts}: {scene_id}")

# @app.cheatcode('Generate screenshot here', 'left', 'left', 'right', 'right')
# def generate_screenshot(scene_id, start_ts):
#     log.info(f"Generate screenshot at {start_ts}: {scene_id}")

def main():
    stash_log.debug(f'Start')

    json_input_str = os.environ.get('STASH_INPUT')
    if not json_input_str:
        stash_log.error(f'Fatal error: STASH_INPUT environment variable not set')
        raise Exception(f'Fatal error: STASH_INPUT environment variable not set')

    if json_input_str == 'dev':
        json_input_str = json.dumps({
            'server_connection': {
                'Scheme': 'http',
                'Host': 'localhost',
                'Port': 9999,
                'PluginDir': os.path.dirname(os.path.abspath(__file__)),
            },
            'args': {},
        })

    try:
        json_input = json.loads(json_input_str)
    except json.JSONDecodeError as e:
        stash_log.error(f'Fatal error: STASH_INPUT environment variable not correct: {json_input_str!r}')
        raise Exception(f'STASH_INPUT environment variable not correct: {json_input_str!r}') from e

    plugin_args = json_input['args']
    server_connection = json_input['server_connection']
    plugin_dir = server_connection['PluginDir']

    log_file = f'{plugin_dir}/log.txt'
    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    global log
    log = logging.getLogger(__name__ if __name__ != '__main__' else 'VRoom')
    log.setLevel(logging.DEBUG)
    log.addHandler(file_handler)
    
    stream_handler = None
    if sys.stdout.isatty():
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        log.addHandler(stream_handler)

    # Add handler to all loggers in the stash_vroom namespace, ensuring they're at DEBUG level
    for logger_name, logger_obj in logging.root.manager.loggerDict.items():
        if logger_name.startswith('stash_vroom') and isinstance(logger_obj, logging.Logger):
            logger_obj.setLevel(logging.DEBUG)
            logger_obj.addHandler(file_handler)
            if stream_handler:
                logger_obj.addHandler(stream_handler)

    log.info('Stash plugin: Ready')
    log.debug(f'Input JSON: {json.dumps(json_input)}')

    api_url = server_connection['Scheme'] + '://' + server_connection['Host'] + ':' + str(server_connection['Port']) + '/graphql'
    headers = None

    session_cookie = server_connection.get('SessionCookie')
    if session_cookie:
        headers = { 'Cookie': f"{session_cookie['Name']}={session_cookie['Value']}" }

    log.info('Run')
    app.run(stash_url=api_url, stash_headers=headers)  # Output: "Listening on http://0.0.0.0:5000"

    log.info('Clean server exit')
    sys.exit(0)

if __name__ == '__main__':
    main()