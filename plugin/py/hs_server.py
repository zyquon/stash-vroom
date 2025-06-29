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

# HereSphere server for the VRoom plugin.

import os
import sys
import json
import logging

import util
import stash_log

# import stash_vroom
from stash_vroom.heresphere import HereSphere

log = logging.getLogger(__name__)

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
    log.debug(f'Start')
    return server()

def server():
    api_url = util.get_stash_input_url()
    headers = util.get_stash_input_headers()
    log.debug(f'Headers {"populated" if headers else "empty"} for API: {api_url}')

    app.run(stash_url=api_url, stash_headers=headers)  # Output: "Listening on http://0.0.0.0:5000"
    log.info('Clean server exit')

if __name__ == '__main__':
    main()