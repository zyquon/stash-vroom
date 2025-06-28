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

log = None

app = HereSphere('Stash-VRoom')
app.state = {}

app.state['scenes_by_id'] = {} # scene_id -> scene
app.state['library'] = []

# @app.saved_scene_filters.events.inserted.connect
# def on_saved_filter_inserted(i, saved_filter):
#     # log.debug(f'Saved filter inserted at {i}: {saved_filter!r}')
#     pass

# @app.saved_scene_filters.events.removed.connect
# def on_saved_filter_removed(i, saved_filter):
#     # log.debug(f'Saved filter removed at {i}: {saved_filter!r}')
#     pass

@app.saved_filter.connect
def on_scene_filter(name, find_filter, scene_filter, scenes):
    log.debug(f'Saved filter named {name!r} with {len(scenes)} initial scenes: {find_filter!r} and {scene_filter!r}')

    library_names = [ X['name'] for X in app.state['library'] ]
    if name in library_names:
        log.debug(f'Skip known saved filter: {name!r}')
        return

    new_lib = {'name':name, 'list':[]}
    app.state['library'].append(new_lib)
    app.state['library'].sort(key=lambda x: x['name'])

    # scenes_list = app._vroom_scenes_by_filter[name]
    @scenes.events.inserted.connect
    def on_scene_in_filter(i, scene):
        log.debug(f'Scene {scene["id"]} inserted at {i} in filter {name!r}: {scene!r}')
        app.state['scenes_by_id'][scene['id']] = scene
        new_lib['list'].insert(i, scene)

# @app.saved_filter_scene.connect
def on_scene_in_filter(filter_name, scene):
    log.debug(f'Scene in filter {filter_name!r}: {find_filter!r}')

    # This call seems faster for a bulk pull of unknown scenes in one round-trip.
    # It could be optimized with a query fragment only for scene ID, then querying for only the unknown scenes in a followup call.
    res = app.stash_client.scenes(find_filter=find_filter, scene_filter=scene_filter)
    res = res.model_dump()

    log.debug(f'Scenes in filter {filter_name!r}: {res["findScenes"]["count"]}')
    scenes = res['findScenes']['scenes']
    for scene in scenes:
        log.debug(f'Found scene {scene["id"]}: {scene["title"]}')

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
    
    # Set up logging.
    server_connection = json_input['server_connection']
    plugin_dir = server_connection['PluginDir']

    log_file = f'{plugin_dir}/plugin/log/vroom-log.txt'
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
            if logger_name.startswith('stash_vroom'): # TODO: Or this namespace too.
                logger_obj.setLevel(logging.DEBUG)
                logger_obj.addHandler(file_handler)
                if stream_handler:
                    logger_obj.addHandler(stream_handler)

    log.info('Stash plugin: Ready')

    # Now route to the correct task to run.
    plugin_args = json_input.get('args', {})

    if not plugin_args:
        return server(json_input)

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

    if action == 'enable':
    #     from stash_vroom.ffmpeg_wrapper import enable_ffmpeg_wrapper
    #     enable_ffmpeg_wrapper()
    #     stash_log.info('FFmpeg wrapper enabled')
    # elif action == 'disable':
    #     from stash_vroom.ffmpeg_wrapper import disable_ffmpeg_wrapper
    #     disable_ffmpeg_wrapper()
    #     stash_log.info('FFmpeg wrapper disabled')
    else:
        raise ValueError(f'Unknown FFmpeg wrapper action: {action}')

def server(json_input):

    api_url = util.get_stash_input_url()
    headers = util.get_stash_input_headers()

    log.info('Run')
    app.run(stash_url=api_url, stash_headers=headers)  # Output: "Listening on http://0.0.0.0:5000"

    log.info('Clean server exit')
    sys.exit(0)

if __name__ == '__main__':
    main()