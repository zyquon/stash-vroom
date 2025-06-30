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
import logging
import logging.handlers

import util
import stash_log
stash_log.debug(f'Load')

try:
    import stash_vroom
    from stash_vroom.heresphere import HereSphere
except ImportError as e:
    stash_log.error(f'Failed to load VRoom Python package: {e}')
    raise

import hs_server

log = None

def main():
    stash_log.debug(f'Start')

    try:
        json_input = util.get_stash_input()
    except Exception as e:
        stash_log.error(f'Fatal error: {e}')
        raise
    
    # Set up logging.
    server_connection = json_input['server_connection']
    plugin_dir = server_connection['PluginDir']

    log_dir = f'{plugin_dir}/plugin/log'
    log_file = f'{log_dir}/vroom-log.txt'
    os.makedirs(log_dir, exist_ok=True)

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
        if isinstance(logger_obj, logging.Logger):
            if logger_name.startswith('stash_vroom.') or logger_name in ('hs_server', 'util'):
                logger_obj.setLevel(logging.DEBUG)
                logger_obj.addHandler(file_handler)
                if stream_handler:
                    logger_obj.addHandler(stream_handler)

    log.info('Stash plugin: Ready')

    # Now route to the correct task to run.
    plugin_args = json_input.get('args', {})

    if not plugin_args:
        result = hs_server.main()
        log.debug(f'hs_server.main() returned: {result!r}')
        sys.exit(result if isinstance(result, int) else 0)

    if plugin_args.get('task') == 'ffmpeg-wrapper' and 'action' in plugin_args:
        action = plugin_args['action']
        return set_ffmpeg_wrapper(action)

    raise NotImplementedError(f'Unknown plugin arguments: {plugin_args}')

def set_ffmpeg_wrapper(action):
    stash_log.debug(f'Set FFmpeg wrapper action: {action}')

    api_url = util.get_stash_input_url()
    api_headers = util.get_stash_input_headers()
    client = stash_vroom.stash.init(api_url, api_headers)

    res = client.configuration().model_dump()
    log.debug(f'Response:\n{json.dumps(res, indent=2)}')

    ffmpegPath = res['configuration']['general']['ffmpegPath']
    parallelTasks = res['configuration']['general']['parallelTasks']
    log.debug(f'argv: {sys.argv!r}')

    # if action == 'enable':
    #     from stash_vroom.ffmpeg_wrapper import enable_ffmpeg_wrapper
    #     enable_ffmpeg_wrapper()
    #     stash_log.info('FFmpeg wrapper enabled')
    # elif action == 'disable':
    #     from stash_vroom.ffmpeg_wrapper import disable_ffmpeg_wrapper
    #     disable_ffmpeg_wrapper()
    #     stash_log.info('FFmpeg wrapper disabled')
    # else:
    #    # raise ValueError(f'Unknown FFmpeg wrapper action: {action}')

if __name__ == '__main__':
    main()