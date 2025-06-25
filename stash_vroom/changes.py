# Copyright 2025 Zyquo Onrel
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

"""
This module provides a placeholder for managing scene-related events,
similar to the Node.js EventEmitter object.
"""

import re
import logging
from typing import Callable, Dict, List

log = logging.getLogger(__name__)

class SceneChanges:
    """
    A placeholder class for managing scene-related events.
    """

    def __init__(self, stash_api, blacklist=None):
        self._event_handlers: Dict[str, List[Callable]] = {
            "insert_view": [],
            "delete_view": [],
            "insert_scene": [],
            "delete_scene": []
        }

        self.stash = stash_api
        self.blacklist = blacklist or []

        self.views = []
        self.scenes = {}
        log.info("Initialized SceneChanges")

    def on(self, event_name: str, handler: Callable):
        """
        Register an event handler for a specific event.

        :param event_name: Name of the event
        :param handler: Callable to handle the event
        """
        if event_name not in self._event_handlers:
            raise ValueError(f"Unsupported event: {event_name}")
        self._event_handlers[event_name].append(handler)
        # log.debug(f"Registered handler for event {event_name}: {handler.__name__}")

    def emit(self, event_name: str, *args, **kwargs):
        """
        Trigger an event and call all registered handlers.

        :param event_name: Name of the event
        :param args: Positional arguments to pass to the handlers
        :param kwargs: Keyword arguments to pass to the handlers
        """
        if event_name not in self._event_handlers:
            raise ValueError(f"Unsupported event: {event_name}")
        for handler in self._event_handlers[event_name]:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                log.error(f"Error in handler for event {event_name}: {e}")
                raise
            else:
                log.debug(f"Executed handler for event {event_name}: {handler.__name__}")
    
    def start(self):
        """
        Start the SceneChanges event manager.
        """
        log.info("Start SceneChanges")
        self.boot_scenes()
    
    def boot_scenes(self):
        # Image filtering disabled for now.
        # img_filters = STASH.find_saved_filters(mode='IMAGES')
        # log.debug(f'Image filters found: {len(img_filters)}')
        img_filters = []

        scene_filters = self.stash.find_saved_filters(mode='SCENES')
        log.debug(f'Scene filters found: {len(scene_filters)}')

        all_filters = scene_filters + img_filters

        stash_filters = []
        for flt in all_filters:
            ok_prefixes = r'AA|XP|VR' # Should be just "VR" I think.
            vr_re = r'^\s*(' + ok_prefixes + r')\s*\|\s*(.+?)\s*$'
            match = re.match(vr_re, flt['name'], re.IGNORECASE)
            if match:
                filter_name = match.group(1)
            elif flt['name'].strip().lower() == 'vr':
                filter_name = flt['name'].strip()
            else:
                filter_name = None
            
            if filter_name:
                if flt['name'] in self.blacklist:
                    log.debug(f'Skip blacklisted filter: {filter_name}')
                else:
                    stash_filters.append(flt)

        all_st_scenes = {}
        img_fragment = get_big_image_fragment()
        scene_fragment = get_big_scene_fragment()
        for flt in sorted(stash_filters, key=lambda x: x['name'].lower()):
            kwargs = saved_filter_to_find_scenes_kwargs(flt)

            scenes = []
            images = []

            log.debug(f'Filter: {flt["name"]}')
            if flt.get('mode') == 'IMAGES':
                images = self.stash.find_images(fragment=img_fragment, **kwargs)
            elif '_scene_ids' in flt:
                scenes = self.stash.get_scene(id=flt['_scene_ids'], fragment=scene_fragment)
            elif not all_st_scenes:
                # This API call is slightly faster per call, so it is more useful for a cold start, ideally
                # for an "All" view to pull down most scenes.
                log.debug(f'Get scenes for filter: {flt["name"]}')
                scenes = self.stash.find_scenes(fragment=scene_fragment, **kwargs)
                for scene in scenes:
                    all_st_scenes[ scene['id'] ] = scene
            else:
                # This method is faster to fill in a few scenes by ID.
                scenes = self.stash.find_scenes(fragment='id', **kwargs)
                all_scene_ids = [ X['id'] for X in scenes ]
                unknown_scene_ids = [ X for X in all_scene_ids if X not in all_st_scenes ]
                log.debug(f'View {repr(flt["name"])} returned: {len(all_scene_ids)} IDs, {len(all_scene_ids) - len(unknown_scene_ids)} known, query for {len(unknown_scene_ids)} new')
                new_scenes = self.stash.get_scene(id=unknown_scene_ids, fragment=scene_fragment)

                # Build the scenes list from the known and new scenes, maintaining order.
                for scene_id in all_scene_ids:
                    if scene_id in all_st_scenes:
                        scene = all_st_scenes[scene_id]
                    elif scene_id == new_scenes[0]['id']:
                        scene = new_scenes.pop(0)
                    else:
                        raise Exception(f'Expected scene {scene_id} to be this scene: {new_scenes[0]}')
                    scenes.append(scene)

            for scene in scenes:
                all_st_scenes[ scene['id'] ] = scene

            log.debug(f'Scenes in filter {flt["name"]}: {len(scenes)}')
            log.debug(f'Total scenes known: {len(all_st_scenes)}')

def saved_filter_to_find_scenes_kwargs(flt):
    # TODO: Maybe return the GQL object rather than Stashapp API but this is good enough.
    find_filter = flt['find_filter']
    object_filter = flt['object_filter']
    filter_to_query(object_filter)

    # Always query for the entire data set without paging.
    find_filter['page'] = 1
    find_filter['per_page'] = -1

    # view_id = flt['name']
    kwargs = {
        'f': object_filter,
        'q': find_filter['q'],
        'filter': find_filter,
    }
    return kwargs

def filter_to_query(flt):
    """
    Convert a saved filter object into a query object suitable for finding scenes over GraphQL
    """
    #log.debug(f'Fix filter:\n' + json.dumps(flt, indent=2))
    tag_labels = ['tags', 'performer_tags']
    for tag_label in tag_labels:
        if tag_label in flt:
            original = flt[tag_label]

            flt[tag_label] = {}
            flt[tag_label]['depth'] = original['value']['depth']
            flt[tag_label]['modifier'] = original['modifier']

            if 'items' in original['value']:
                flt[tag_label]['value'] = [ X['id'] for X in original['value']['items'] ]
            if 'excluded' in original['value']:
                flt[tag_label]['excludes'] = [ X['id'] for X in original['value']['excluded'] ]

    if 'studios' in flt:
        modifier = flt['studios'].get('modifier')
        if modifier != 'INCLUDES':
            raise NotImplementedError(f'Modifier must be INCLUDES for now')

        val = flt['studios'].get('value')
        if not val:
            raise ValueError(f'Filter .studios must have .value property')

        depth = val.get('depth')
        if depth != 0:
            raise ValueError(f'Filter .studios depth must be 0')

        excludes = val.get('excluded')
        if not isinstance(excludes, list) or len(excludes) != 0:
            raise ValueError(f'Filter for .studios excludes must be empty')

        studio_ids = [ X['id'] for X in val['items'] ]

        flt['studios'] = {
            'depth': depth,
            'modifier': modifier,
            'excludes': excludes,
            'value': studio_ids,
        }

    if 'is_missing' in flt:
        if isinstance(flt['is_missing'], dict):
            if flt['is_missing']['modifier'] != 'EQUALS':
                raise Exception(f'Unknown is_missing: {flt}')
            flt['is_missing'] = flt['is_missing']['value']

    if 'has_markers' in flt:
        if isinstance(flt['has_markers'], dict):
            if flt['has_markers']['modifier'] != 'EQUALS':
                raise Exception(f'Unknown has_markers: {flt}')
            flt['has_markers'] = flt['has_markers']['value']

    if 'performer_favorite' in flt:
        if flt['performer_favorite']['modifier'] != 'EQUALS':
            raise Exception(f'Unknown performer favorite value: {repr(flt)}')
        flt['performer_favorite'] = flt['performer_favorite']['value'] in ('true', True)

    keys = ['file_count', 'performer_count', 'rating100', 'o_counter']
    for key in keys:
        if key in flt:
            # Convert "value":{"value":N} -> "value":N.
            value = flt[key]['value']
            if isinstance(value, dict) and 'value' in value:
                flt[key]['value'] = value['value']

def get_big_image_fragment():
    fragment = ( ''
        + ' __typename'
        + ' id urls title details rating100 date created_at o_counter'
        + ' paths { thumbnail image } tags { id name }'
        + ' visual_files { __typename ... on ImageFile { basename path size width height } }'
        + ' performers{ id name gender country favorite ethnicity tags{ name }  }'
        + ' studio{ name tags{ id name } parent_studio{ name parent_studio{ name parent_studio{ name } } } }'
        + '' )
    return fragment

def get_big_scene_fragment():
    fragment = (
        ' id urls title details rating100 date created_at o_counter play_count'
        ' studio{ name tags{ id name } parent_studio{ name parent_studio{ name parent_studio{ name } } } }'
        ' paths{ stream screenshot preview }'
        ' files{ format basename size width height duration fingerprints{ type value } }'
        ' performers{ id name gender country favorite ethnicity fake_tits tags{ name }  }'
        ' scene_markers{ id seconds primary_tag{ name } tags{ id name parents{ id name parents{ id name parents{ id name } } } } }'
        ' tags{ id name parents{ id name parents{ id name parents{ id name } } } }'
    )
    return fragment