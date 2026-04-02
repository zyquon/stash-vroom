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

def get_vid_re(extensions=('mp4', 'm4v', 'mkv', 'avi', 'webm', 'flv', 'wmv', 'mov')):
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

def get_ffmpeg_wrapper_path():
    # Return the path to the ffmpeg-vroom CLI script which is defined in pyproject.toml. This function can import any packages it needs to ascertain the script location.
    raise NotImplementedError(f'Getting the path to the entrypoint turned out to be hard') # TODO I think just the sys.executable switched to ffmpeg-vroom should be OK

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
    object_filter = convert_ui_filter(object_filter)
    return json.loads(json.dumps(object_filter)) # Make sure no autogen objects persist.


def convert_ui_filter(flt):
    """Convert Stash UI saved filter format to GraphQL input format.

    The Stash UI stores filters in its own internal representation which
    differs from the GraphQL API input types. This function transforms
    the UI format to valid GraphQL input.
    """
    if not isinstance(flt, dict):
        return flt

    flt = dict(flt)  # shallow copy

    # HierarchicalMultiCriterionInput fields
    # UI: {modifier, value: {depth, items: [{id, label}], excluded: [{id, label}]}}
    # GQL: {modifier, value: [id...], excludes: [id...], depth}
    hierarchical_fields = [
        'tags', 'performer_tags', 'scene_tags', 'studios',
        'parent_tags', 'child_tags', 'parent_studios',
    ]
    for key in hierarchical_fields:
        if key not in flt:
            continue
        orig = flt[key]
        val = orig.get('value', {})
        if not isinstance(val, dict) or ('items' not in val and 'excluded' not in val):
            continue
        result = {'modifier': orig['modifier']}
        result['value'] = [x['id'] for x in val.get('items', [])]
        excluded = val.get('excluded', [])
        if excluded:
            result['excludes'] = [x['id'] for x in excluded]
        if 'depth' in val:
            result['depth'] = _to_int(val['depth'])
        flt[key] = result

    # MultiCriterionInput fields (no depth)
    # UI: {modifier, value: {items: [{id, label}], excluded: [{id, label}]}}
    # GQL: {modifier, value: [id...], excludes: [id...]}
    for key in ['performers', 'galleries', 'groups', 'movies', 'scenes',
                 'containing_groups', 'sub_groups']:
        if key not in flt:
            continue
        orig = flt[key]
        val = orig.get('value', {})
        if not isinstance(val, dict) or ('items' not in val and 'excluded' not in val):
            continue
        result = {'modifier': orig['modifier']}
        result['value'] = [x['id'] for x in val.get('items', [])]
        excluded = val.get('excluded', [])
        if excluded:
            result['excludes'] = [x['id'] for x in excluded]
        flt[key] = result

    # IntCriterionInput fields: {modifier, value: {value: N, value2: M}} -> {modifier, value: N}
    int_fields = [
        'file_count', 'performer_count', 'rating100', 'o_counter',
        'play_count', 'resume_time', 'play_duration', 'duration',
        'tag_count', 'image_count', 'gallery_count', 'performer_age',
        'interactive_speed', 'framerate', 'bitrate', 'weight',
        'scene_count', 'marker_count',
        'height_cm', 'birth_year', 'death_year', 'age', 'penis_length',
        'zip_file_count', 'containing_group_count', 'sub_group_count',
    ]
    for key in int_fields:
        if key not in flt:
            continue
        val = flt[key].get('value')
        if isinstance(val, dict) and 'value' in val:
            flt[key]['value'] = _to_int(val['value'])
            if 'value2' in val and val['value2'] is not None:
                flt[key]['value2'] = _to_int(val['value2'])
        elif isinstance(val, str):
            flt[key]['value'] = _to_int(val)

    # String-as-boolean fields: UI stores {modifier: "EQUALS", value: "true"} -> plain string
    for key in ['is_missing', 'has_markers', 'has_chapters']:
        if key in flt and isinstance(flt[key], dict):
            if flt[key].get('modifier') == 'EQUALS':
                flt[key] = flt[key]['value']

    # Boolean fields: UI stores {modifier: "EQUALS", value: "true"} -> plain bool
    for key in ['organized', 'performer_favorite', 'interactive',
                'favourite', 'ignore_auto_tag']:
        if key in flt and isinstance(flt[key], dict):
            if flt[key].get('modifier') == 'EQUALS':
                flt[key] = flt[key]['value'] in ('true', True)

    # DateCriterionInput fields: {modifier, value: {value: "2024-01-01", value2: "..."}}
    # -> {modifier, value: "2024-01-01", value2: "..."} (flatten nested, drop empty value2)
    date_fields = ['date', 'birthdate', 'death_date', 'scene_date']
    for key in date_fields:
        if key not in flt:
            continue
        val = flt[key].get('value')
        if isinstance(val, dict) and 'value' in val:
            flt[key]['value'] = val['value']
            if val.get('value2'):
                flt[key]['value2'] = val['value2']

    # TimestampCriterionInput fields: same nesting as date, plus normalize
    # space-separated datetime to ISO 8601 (T separator)
    timestamp_fields = ['created_at', 'updated_at', 'last_played_at',
                        'scene_created_at', 'scene_updated_at']
    for key in timestamp_fields:
        if key not in flt:
            continue
        val = flt[key].get('value')
        if isinstance(val, dict) and 'value' in val:
            flt[key]['value'] = _normalize_timestamp(val['value'])
            if val.get('value2'):
                flt[key]['value2'] = _normalize_timestamp(val['value2'])

    # StashIdCriterionInput: {modifier, value: {endpoint, stashID}}
    # -> {modifier, endpoint, stash_id}
    if 'stash_id_endpoint' in flt:
        orig = flt['stash_id_endpoint']
        val = orig.get('value', {})
        if isinstance(val, dict) and 'stashID' in val:
            flt['stash_id_endpoint'] = {
                'modifier': orig['modifier'],
                'endpoint': val.get('endpoint', ''),
                'stash_id': val['stashID'],
            }

    # PhashDistanceCriterionInput: {modifier, value: {value: "hash", distance: N}}
    # -> {modifier, value: "hash", distance: N}
    if 'phash_distance' in flt:
        orig = flt['phash_distance']
        val = orig.get('value')
        if isinstance(val, dict) and 'distance' in val:
            flt['phash_distance'] = {
                'modifier': orig['modifier'],
                'value': val['value'],
                'distance': _to_int(val['distance']),
            }

    # PHashDuplicationCriterionInput: {modifier, value: "true"/"false"}
    # -> {duplicated: bool}
    if 'duplicated_phash' in flt:
        orig = flt['duplicated_phash']
        if isinstance(orig, dict) and 'value' in orig:
            flt['duplicated_phash'] = {
                'duplicated': orig['value'] in ('true', True),
            }

    # OrientationCriterionInput: {modifier, value: [enum...]}
    # -> {value: [enum...]}  (modifier stripped)
    if 'orientation' in flt:
        orig = flt['orientation']
        if isinstance(orig, dict) and isinstance(orig.get('value'), list):
            flt['orientation'] = {'value': orig['value']}

    # GenderCriterionInput: {modifier, value: [enum...] | "enum"}
    # -> {modifier, value_list: [enum...]}  (field rename + legacy single-string)
    if 'gender' in flt:
        orig = flt['gender']
        if isinstance(orig, dict):
            val = orig.get('value')
            if isinstance(val, str):
                val = [val]
            flt['gender'] = {'modifier': orig['modifier'], 'value_list': val}

    return flt


def _normalize_timestamp(val):
    """Normalize space-separated datetime to ISO 8601 T separator."""
    if isinstance(val, str) and ' ' in val:
        return val.replace(' ', 'T', 1)
    return val


def _to_int(val):
    """Coerce string-encoded integers from UI format to int."""
    if isinstance(val, str):
        try:
            return int(val)
        except ValueError:
            return val
    return val