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
This module has common and frequently-used functions, which have no big dependencies.
"""

import os
import re
import copy
import json
import logging

log = logging.getLogger(__name__)

SCRIPT_PATH = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)

def get_vid_re(extensions=('mp4', 'm4v', 'mkv', 'avi', 'webm', 'wmv', 'mov')):
    """
    Return a regular expression pattern to match file extensions.

    This is useful both for examining Python strings and also to submit to Stash as
    to find scenes with a regex filter. That is why this function returns a string and not
    a Python regex object.

    :param extensions: Optional list of 
    :return: A regex pattern that matches video file extensions.
    :rtype: str
    """

    if isinstance(extensions, str):
        extensions = [ extensions ]
    
    if isinstance(extensions, (tuple, list)):
        extensions = [ X for X in extensions if X ] # Remove empty strings
        extensions = list(dict.fromkeys(extensions)) # Remove duplicates

    extensions = [ re.escape(X) for X in extensions ]
    extensions = '|'.join(extensions)
    return r'\.(' + extensions + r')$'

def get_font_dirpath():
    return f'{SCRIPT_DIR}/fonts'

def saved_filter_to_find_filter(saved_filter):
    find_filter = saved_filter['find_filter']
    find_filter = copy.deepcopy(find_filter)

    # Always query for the entire data set without paging.
    find_filter['page'] = 1
    find_filter['per_page'] = -1
    return json.loads(json.dumps(find_filter)) # Make sure no autogen objects persist.

def saved_filter_to_scene_filter(saved_filter):
    object_filter = saved_filter['object_filter']
    object_filter = copy.deepcopy(object_filter)
    fix_object_filter(object_filter)
    return json.loads(json.dumps(object_filter)) # Make sure no autogen objects persist.

def fix_object_filter(flt):
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