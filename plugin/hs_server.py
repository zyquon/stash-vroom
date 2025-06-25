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
    from stash_vroom.heresphere import HereSphere
except ImportError as e:
    stash_log.error(f'Failed to load Stash-VRoom Python package: {e}')
    raise

log = None

app = HereSphere('Stash-VRoom')

# @app.saved_scene_filters.events.inserted.connect
# def on_saved_filter_inserted(i, saved_filter):
#     # log.debug(f'Saved filter inserted at {i}: {saved_filter!r}')
#     pass

# @app.saved_scene_filters.events.removed.connect
# def on_saved_filter_removed(i, saved_filter):
#     # log.debug(f'Saved filter removed at {i}: {saved_filter!r}')
#     pass

@app.new_scene_filter.connect
def on_new_scene_filter(name, find_filter, scene_filter):
    log.debug(f'Saved filter named {name!r}: {find_filter!r} and {scene_filter!r}')

# @app.on_eoubleclick()
# def on_doubleclick(scene_id, start_ts):
#     log.info(f"Double-click scene at {start_ts}: {scene_id}")

# @app.cheatcode('Generate screenshot here', 'left', 'left', 'right', 'right')
# def generate_screenshot(scene_id, start_ts):
#     log.info(f"Generate screenshot at {start_ts}: {scene_id}")

def main():
    stash_log.debug(f'Start')

    try:
        json_input = util.get_stash_input()
    except Exception as e:
        stash_log.error(f'Fatal error: {e}')
        raise

    plugin_args = json_input['args']
    server_connection = json_input['server_connection']
    plugin_dir = server_connection['PluginDir']

    log_file = f'{plugin_dir}/plugin/log.txt'
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

    api_url = util.get_stash_input_url()
    headers = util.get_stash_input_headers()

    log.info('Run')
    app.run(stash_url=api_url, stash_headers=headers)  # Output: "Listening on http://0.0.0.0:5000"

    log.info('Clean server exit')
    sys.exit(0)

if __name__ == '__main__':
    main()