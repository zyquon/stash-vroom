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

# Stash plugin miscellaneous utilities.

import os
import json

STASH_INPUT = None

def get_stash_input():
    global STASH_INPUT
    if STASH_INPUT is not None:
        return STASH_INPUT

    json_input_str = os.environ.get('STASH_INPUT')
    if not json_input_str:
        raise Exception(f'Fatal error: STASH_INPUT environment variable not set')

    if json_input_str == 'dev':
        json_input_str = json.dumps({
            'server_connection': {
                'Scheme': 'http',
                'Host': 'localhost',
                'Port': 9999,
                'PluginDir': os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            },
            'args': {},
        })

    try:
        json_input = json.loads(json_input_str)
    except json.JSONDecodeError as e:
        raise Exception(f'STASH_INPUT environment variable not correct: {json_input_str!r}') from e
    
    STASH_INPUT = json_input
    return STASH_INPUT

def get_stash_input_url():
    json_input = get_stash_input()
    # plugin_args = json_input['args']
    server_connection = json_input['server_connection']
    plugin_dir = server_connection['PluginDir']

    url = server_connection['Scheme'] + '://' + server_connection['Host'] + ':' + str(server_connection['Port']) + '/graphql'
    return url

def get_stash_input_headers():
    headers = None

    json_input = get_stash_input()
    server_connection = json_input['server_connection']

    session_cookie = server_connection.get('SessionCookie')
    if session_cookie:
        headers = { 'Cookie': f"{session_cookie['Name']}={session_cookie['Value']}" }
    
    return headers