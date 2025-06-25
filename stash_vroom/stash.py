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
Stash API support
"""

import os
import socket
import logging
import asyncio
import ipaddress
import urllib.parse

from . import util
from . import stash_client

log = logging.getLogger(__name__)

SCRIPT_PATH = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)

STASH_HOST = None # os.environ.get('STASH_HOST', '127.0.0.1')
STASH_PORT = None
STASH_SCHEME = None
STASH_IP = None
STASH_API_KEY = None

API = None

def get_api_key(default=None):
    global STASH_API_KEY
    if STASH_API_KEY:
        return STASH_API_KEY

    if isinstance(default, str) and default:
        # log.debug(f'Use default API key: {default}')
        STASH_API_KEY = default
        return default

    api_key = os.environ.get('STASH_API_KEY')
    if isinstance(api_key, str) and api_key:
        STASH_API_KEY = api_key
        return api_key

    log.debug(f'No STASH_API_KEY environment variable set; trying to read from config file')
    config_filepath = os.path.expanduser(f'~/.stash/config.yml')
    try:
        with open(config_filepath, 'r') as f:
            config = f.read()
    except FileNotFoundError:
        raise Exception(f'Must set environment variable: STASH_API_KEY or provide a valid config file at {config_filepath}')

    for line in config.split('\n'):
        line = line.strip()
        if line.startswith('api_key:'):
            api_key = line.split('api_key:')[1].strip()
            STASH_API_KEY = api_key
            return api_key

    raise Exception(f'Must set environment variable: STASH_API_KEY or provide a valid config file at {config_filepath}')

def init(stash_url='http://127.0.0.1:9999/graphql', stash_headers=None, validate=True):
    """Initialize a connection to the Stash API.
    
    This function initializes a connection to the Stash server, validates
    the connection if requested, and returns a StashInterface object.
    
    :param stash_url: The URL of the Stash server, This will be used to generate links in the web UI too.
    :type stash_url: str
    :param validate: Whether to validate the connection by checking version, stashbox connections and ffmpeg path
    :type validate: bool
    :raises Exception: If hostname cannot be resolved, API key is missing, or validation fails
    :return: A StashInterface instance for interacting with the Stash API
    :rtype: [`StashInterface`](stash_vroom/stash.py)
    
    If the Stash API connection is already initialized, returns the existing instance.
    
    When validate is True (default), the function will:
    - Check that the hostname resolves to a valid IP address
    - Verify the API connection by checking Stash version
    - Check StashBox connections
    - Verify and potentially update the ffmpeg path

    .. tip::
        Often, you can use the name of the machine running Stasah, appended with ``.local``, e.g. ``mypc.local``.
    
    .. important::
        Local machines with ``.local`` names are convenient on PCs, Macs, and mobile devices.
        Unfortunately, on Quest 3 (at least), HereSphere's web browser cannot use ``.local`` URLs.
        When using HereSphere, use the IP address for the URL, e.g. ``http://192.168.0.<some number>:5000``.

    """
    global API
    global STASH_IP
    global STASH_SCHEME
    global STASH_HOST
    global STASH_PORT
    global STASH_SCHEME

    if API:
        return API

    # Figure out the stash_hostname from the stash_url using a url parsing module.
    parsed_url = urllib.parse.urlparse(stash_url)
    stash_hostname = parsed_url.hostname

    if STASH_HOST is None:
        STASH_HOST = stash_hostname
    if STASH_PORT is None:
        STASH_PORT = parsed_url.port
    if STASH_SCHEME is None:
        STASH_SCHEME = parsed_url.scheme

    if validate:
        ips = get_all_ip_addresses(STASH_HOST)
        log.debug(f'Local IPs: {ips}')
        for ip in ips:
            net = get_internal_net(ip)
            if net:
                log.debug(f'- Ignore internal net: {net}')
            else:
                STASH_IP = ip
        if not STASH_IP:
            raise Exception(f'Cannot get an IP for stash host: {STASH_HOST}')

    if not stash_headers:
        api_key = get_api_key()
        stash_headers = {'ApiKey': api_key}

    stashapi = stash_client.Stash(stash_url, headers=stash_headers)

    if validate:
        try:
            res = stashapi.version()
            res = res.model_dump()
        except stash_client.exceptions.GraphQLClientHttpError as e:
            log.error(f'ERROR: Cannot connect to Stash API at {origin()}: {e}')
            raise e

        stash_version = res['version']['version']
        if stash_version:
            log.debug(f'Stash version: {stash_version}')
        else:
            raise Exception(f'ERROR: Cannot get Stash version; possible auth problem')

        try:
            res = stashapi.configuration()
            res = res.model_dump()
        except stash_client.exceptions.GraphQLClientHttpError as e:
            log.error(f'ERROR: Cannot connect to Stash API at {origin()}: {e}')
            raise e

        config = res['configuration']
        apis = config['general']['stashBoxes']
        log.debug(f'StashBox APIs: {len(apis)}')
        for api in apis:
            log.debug(f'- {api["name"]} -> {api["endpoint"]}')

        ffmpeg_wrapper_path = f'{SCRIPT_DIR}/ffmpeg.sh'
        if config['general']['ffmpegPath'] == ffmpeg_wrapper_path:
            log.debug(f'Stash is using VRoom ffmpeg path: {ffmpeg_wrapper_path}')
        else:
            log.info(f'Stash is not using VRoom ffmpeg path: {repr(config["general"]["ffmpegPath"])} is not {ffmpeg_wrapper_path}')
            # Updating the config is disabled until things are stable and the ffmpeg wrapper is more proven.
            # In fact it should probably be a plugin task activated by the user in the UI.
            #
            # new_config = stashapi.configure_general({'ffmpegPath':ffmpeg_wrapper_path}, fragment='ffmpegPath')
            # if new_config['ffmpegPath'] != ffmpeg_wrapper_path:
            #     raise Exception(f'Failed to set ffmpeg path: {config}')
            # log.debug(f'- Good ffmpeg update: {ffmpeg_wrapper_path}')

    API = stashapi
    return stashapi

def get_internal_net(ip):
    ip = ipaddress.IPv4Address(ip)
    internal_nets = [ '169.254.0.0/16', '172.16.0.0/12' ]
    for internal_net in internal_nets:
        network = ipaddress.IPv4Network(internal_net)
        if ip in network:
            return internal_net
    return None

def get_all_ip_addresses(hostname):
    try:
        addresses = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise Exception(f'Unable to resolve hostname: {hostname}')

    #print(f'XXX addresses: {repr(addresses)}')
    result = [ addr[-1][0] for addr in addresses ]
    result = list(set(result)) # Dedupe
    return result

def origin():
    return f'{STASH_SCHEME}://{STASH_HOST}:{STASH_PORT}'

# class StashInterface(stashapi.stashapp.StashInterface):
class StashInterface:
    def find_job(self, job_id):
        result = super().find_job(job_id)
        if not result:
            raise Exception(f'Bad result looking for job ID {repr(job_id)}: {repr(result)}')
        if 'progress' in result and result['progress'] is None:
            result['progress'] = 0.0
        return result

    def update(self, update):
        scene_id = update['id']
        if not scene_id:
            raise ValueError(f'Update must have a scene ID "id" field')
        result = self.update_scene(update)
        if result != scene_id:
            raise Exception(f'Error updating scene {repr(update)}: {repr(result)}')

    def scan(self, paths, flags=None):
        log.debug(f'  - Metadata scan (flags {flags}): {paths}')
        if isinstance(paths, str):
            paths = [ paths ]
        if flags is None:
            flags = scan_flags()
        jobid = self.metadata_scan(paths=paths, flags=flags)
        result = block_for_job(jobid, label='Scan paths: {paths}')
        if not result:
            raise Exception(f'Error scaning paths {paths}: {repr(result)}')

    def get_directory(self, dirpath):
        log.debug(f'Get directory: {repr(dirpath)}')

        query = '''
        query Directory($path: String!) {
            directory(path: $path) {
                path
                parent
                directories
            }
        }'''
        variables = {
            'path': dirpath,
        }

        #log.debug(query.strip() + f'\nfilter = {repr(variables["filter"])}' + f'\nids: {variables["ids"]}') # XXX
        result = self.call_GQL(query, variables)
        directory = result['directory']
        log.debug(f'Find directory by path {repr(dirpath)}: {repr(directory)}')
        return directory

    def get_image(self, id, fragment=None):
        if not fragment:
            fragment = 'id tags{ id name } visual_files { __typename ... on ImageFile { id path } }'
        return self.get_image_by_id(id, fragment=fragment)

    def get_image_by_id(self, image_id, fragment, null=False):
        # log.debug(f'- Find image with tags={repr(None)} by ID: {repr(image_id)}')
        if not isinstance(image_id, int):
            image_id = int(image_id)

        query = f'''
        query FindImage($id: ID!) {{
            findImage(id: $id) {{
                {fragment}
            }}
        }}'''
        kwargs = {
            'id': image_id,
        }

        #log.debug(query.strip() + f'\nfilter = {repr(kwargs["filter"])}' + f'\nids: {kwargs["ids"]}') # XXX
        result = self.call_GQL(query, kwargs)
        image = result['findImage']
        # log.debug(f'Find image by ID: {repr(image)}')
        return image

    def get_performer(self, id=None, name=None, tags=None, null=False, fragment=None):
        if not fragment:
            fragment = 'id name favorite gender ethnicity country fake_tits o_counter image_path alias_list urls tags{ id name }'

        tag_ids = []
        for i, tag in enumerate(tags or []):
            result = self.find_tag(tag, on_multiple=stashapi.stashapp.OnMultipleMatch.RETURN_LIST)
            if isinstance(result, list):
                raise Exception(f'No unique tag matche for search id={repr(id)} name={repr(name)}: {repr(result)}')
            tag_id = result['id']
            tag_ids.append(tag_id)

        if id:
            return self.get_performer_by_id(perf_id=id, fragment=fragment, tags=tag_ids, null=null)
        else:
            return self.get_performer_by_name(name=name, fragment=fragment, tags=tag_ids, null=null)

    def get_performer_by_id(self, perf_id, fragment, tags=None, null=False):
        # log.debug(f'- Find performer with tags={repr(tags)}ty ID: {repr(perf_id)}')
        if not isinstance(perf_id, int):
            perf_id = int(perf_id)

        query = f'''
        query FindPerformer($id: ID!) {{
            findPerformer(id: $id) {{
                {fragment}
            }}
        }}'''
        variables = {
            'id': perf_id,
        }

        #log.debug(query.strip() + f'\nfilter = {repr(variables["filter"])}' + f'\nids: {variables["ids"]}') # XXX
        result = self.call_GQL(query, variables)
        performer = result['findPerformer']
        # log.debug(f'Find performer by ID: {repr(performer)}')
        return performer

    def get_performer_by_name(self, name, fragment, tags=None, null=False):
        # log.debug(f'- Find performer with tags={repr(tags)} by name: {repr(name)}')
        query = { 'aliases': { 'modifier':'EQUALS', 'value':name} }
        if tags:
            query['tags'] = { 'modifier':'INCLUDES_ALL', 'value':tags }

        performers = self.find_performers(query)
        if performers:
            # log.debug(f'- Found performer by name: {repr(name)}')
            return performers[0]

        log.debug(f'- Find performer with tags={repr(tags)} by alias: {repr(name)}')
        query = { 'name': { 'modifier':'EQUALS', 'value':name} }
        if tags:
            query['tags'] = { 'modifier':'INCLUDES_ALL', 'value':tags }

        performers = self.find_performers(query, fragment=fragment)
        if performers:
            # log.debug(f'- Found performer by alias: {repr(name)}')
            return performers[0]

        if null:
            return None

        raise Exception(f'Could not find performer: {repr(name)}')

    def update_performer(self, update):
        query = """
            mutation PerformerUpdate($input:PerformerUpdateInput!) {
                performerUpdate(input: $input) {
                    id
                }
            }
        """
        result = self.call_GQL(query, {'input':update})
        if result['performerUpdate']['id'] == update['id']:
            log.debug(f'- Good performer update')
        else:
            raise Exception(f'Bad result updating performer {repr(update)}: {repr(result)}')

    def get_studio(self, fragment, id=None, name=None, null=False):
        if id and name:
            raise ValueError(f'Must only pass id or name')
        elif id is None and name is None:
            raise ValueError(f'Must pass either id or name')
        elif id or isinstance(id, (list, tuple)):
            return self.get_studios_by_ids(id, fragment, null=null)
        elif name or isinstance(name, (list, tuple)):
            return self.get_studios_by_names(name, fragment, null=null)
        else:
            raise ValueError(f'Bad id and name values: id={repr(id)} name={repr(name)}')

    def get_scene(self, fragment, id=None, path=None, null=False):
        if id and path:
            raise ValueError(f'Must only pass id or path')
        elif id is None and path is None:
            raise ValueError(f'Must pass either id or path')
        elif id or isinstance(id, (list, tuple)):
            return self.get_scenes_by_ids(id, fragment, null=null)
        elif path or isinstance(path, (list, tuple)):
            return self.get_scenes_by_paths(path, fragment, null=null)
        else:
            raise ValueError(f'Bad id and path values: id={repr(id)} path={repr(path)}')

    def get_studios_by_ids(self, ids, fragment, null=False):
        raise NotImplementedError(f'Get studio by ID not implemented: {ids}')

    def get_scenes_by_ids(self, ids, fragment, null=False):
        return_scalar = isinstance(ids, (str, int)) # Caller passing a string means return the first match.

        scene_ids = ids
        if isinstance(scene_ids, str):
            scene_ids = [ scene_ids ]

        if not scene_ids:
            log.debug(f'No scene IDs to query')
            return None if return_scalar else []

        query = f'''
        query FindScenes($ids: [ID!], $filter: FindFilterType!) {{
            findScenes(ids: $ids, filter: $filter) {{
                scenes {{
                    {fragment}
                }}
            }}
        }}'''
        variables = {
            'ids': scene_ids,
            'filter': {'per_page': -1},
        }

        #log.debug(query.strip() + f'\nfilter = {repr(variables["filter"])}' + f'\nids: {variables["ids"]}') # XXX
        if null:
            log.warning(f'get_scenes_by_ids with null=True not yet implemented; GQL call will throw for an unknown ID')
        result = self.call_GQL(query, variables)
        scenes = result['findScenes']['scenes']
        return scenes[0] if return_scalar else scenes

    def get_studios_by_names(self, names, fragment, null=False):
        want_scalar = isinstance(names, str)
        if isinstance(names, str):
            names = [ names ]

        result = []
        for name in names:
            studio_filter = {'name': {'modifier':'EQUALS', 'value':name} }
            studios = self.find_studios(studio_filter, fragment=fragment)
            if not studios:
                log.debug(f'- Fallback query studios by alias: {name}')
                studio_filter = {'aliases': {'modifier':'EQUALS', 'value':name} }
                studios = self.find_studios(studio_filter, fragment=fragment)

            if not studios and not null:
                raise ValueError(f'No studio with name: {repr(name)}')
            elif not studios and null:
                result.append(None)
            elif len(studios) > 1:
                raise Exception(f'Multiple studio results for name search {repr(name)}: {studios}')
            else:
                result.append(studios[0])

        return result[0] if want_scalar else result

    # TODO: These two methods could be generalized into some kind of get_objects, then support all major data types.
    def get_scenes_by_paths(self, paths, fragment, null=False):
        want_scalar = isinstance(paths, str)
        if isinstance(paths, str):
            paths = [ paths ]

        result = []
        for path in paths:
            scene_filter = {'path': {'modifier':'EQUALS', 'value':path} }
            scenes = self.find_scenes(scene_filter, fragment=fragment)
            if not scenes and not null:
                raise ValueError(f'No scenes with path: {repr(path)}')
            elif not scenes and null:
                result.append(None)
            elif len(scenes) > 1:
                raise Exception(f'Bad scene result for path {repr(path)}: {scenes}')
            else:
                result.append(scenes[0])

        return result[0] if want_scalar else result

    def get_logs(self, fragment='time level message'):
        query = f"""
            query Logs {{
                logs {{
                    {fragment}
                }}
            }}
        """
        result = self.call_GQL(query)
        return result['logs']

    def get_jobs(self, fragment='id status description progress startTime endTime error subTasks'):
        query = f"""
            query Jobs {{
                jobQueue {{
                    {fragment}
                }}
            }}
        """
        result = self.call_GQL(query)
        return result['jobQueue']

    def add_O_history(self, scene_id, timestamps):
        if isinstance(scene_id, dict):
            scene_id = scene_id['id']

        times = []
        for ts in timestamps:
            ts = util.ts_to_utc_str(ts)
            times.append(ts)

        scene_id = str(scene_id)
        log.debug(f'Add scene {scene_id} O history: {repr(times)}')
        kwargs = {'id':scene_id, 'times':times}
        query = """
            mutation SceneAddO($id:ID!, $times:[Timestamp!]) {
                sceneAddO(id:$id, times:$times) {
                    count
                    history
                }
            }
        """

        result = self.call_GQL(query, kwargs)
        return result['sceneAddO']

    def increment(self, scene_id):
        if isinstance(scene_id, dict):
            if 'id' in scene_id:
                scene_id = scene_id['id']

        if isinstance(scene_id, str):
            pass
        elif isinstance(scene_id, int) or isinstance(scene_id, float):
            scene_id = str(scene_id)
        else:
            raise Exception(f'Bad scene ID: {repr(scene_id)}')

        kwargs = {'id':scene_id}
        query = """
            mutation SceneAddO($id: ID!) {
                sceneAddO(id: $id) {
                    count
                    history
                }
            }
        """

        result = self.call_GQL(query, kwargs)
        return result['sceneAddO']

    def set_scene_play(self, scene_or_id, *play_timestamps):
        scene_id = str(scene_or_id) if isinstance(scene_or_id, (str, int)) else str(scene_or_id['id'])
        times = [ util.ts_to_utc_str(X) for X in play_timestamps ]

        kwargs = {'id':scene_id, 'times':times}
        query = """
            mutation SceneAddPlay($id: ID!, $times: [Timestamp!]) {
                sceneAddPlay(id: $id, times: $times) {
                    count
                    history
                }
            }
        """
        log.debug(f'Set scene {scene_id} play: {repr(times)}')
        result = self.call_GQL(query, kwargs)
        return result['sceneAddPlay']

    def screenshot_at_time(self, scene_or_id, at_seconds=0):
        scene_id = str(scene_or_id) if isinstance(scene_or_id, (str, int)) else scene_or_id['id']
        if not isinstance(at_seconds, (int, float)):
            raise ValueError(f'at_seconds must be a number: {repr(at_seconds)}')

        kwargs = {'id': scene_id, 'at': at_seconds}
        query = """
            mutation SceneGenerateScreenshot($id: ID!, $at: Float) {
                sceneGenerateScreenshot(id: $id, at: $at)
            }
        """
        log.debug(f'Generate screenshot for scene {scene_id} at time: {at_seconds}')
        result = self.call_GQL(query, kwargs)
        return result['sceneGenerateScreenshot']

    def configure_general(self, config, fragment):
        log.debug(f'Update general config: {repr(config)}')
        query = f"""
            mutation ConfigureGeneral($input: ConfigGeneralInput!) {{
                configureGeneral(input:$input) {{
                    {fragment}
                }}
            }}
        """
        result = self.call_GQL(query, {'input':config})
        result = result['configureGeneral']
        return result

    def update_scene_marker_fix(self, gql_input, fragment='id title seconds primary_tag { id name } tags { id name }'):
        query = f"""
            mutation SceneMarkerUpdate($input: SceneMarkerUpdateInput!) {{
                sceneMarkerUpdate(input:$input) {{
                    {fragment}
                }}
            }}
        """
        result = self.call_GQL(query, {'input':gql_input})
        result = result['sceneMarkerUpdate']
        return result

    def set_primary_file(self, scene_id, local_file_id):
        # Can't use .update_scene because it is hard-coded to return only scene ID. We need the updated file order too.
        update = {'id':scene_id, 'primary_file_id':local_file_id}
        query = """
            mutation sceneUpdate($input: SceneUpdateInput!) {
                sceneUpdate(input: $input) {
                    id
                    files {
                        id
                        path
                        size
                        width
                        height
                        fingerprints { ...Fingerprint }
                    }
                }
            }
        """

        result = self.call_GQL(query, {'input':update})
        return result['sceneUpdate']['files']

    def _frag_saved_filter(self):
        return """
            fragment SavedFilterData on SavedFilter {
                id
                mode
                name
                find_filter {
                    q
                    page
                    per_page
                    sort
                    direction
                }
                object_filter
                ui_options
            }
        """

    def find_default_filter(self, mode='SCENES'):
        query = """
            query DefaultFilter($mode: FilterMode!) {
                findDefaultFilter(mode: $mode) {
                    ...SavedFilterData
                }
            }
        """
        query += f'\n\n' + self._frag_saved_filter()
        result = self.call_GQL(query, {'mode':mode})
        return result['findDefaultFilter']

    def find_saved_filters(self, default=False, mode='SCENES'):
        query = """
            query SavedFilters($mode: FilterMode!) {
                findSavedFilters(mode: $mode) {
                    ...SavedFilterData
                }
            }
        """
        query += f'\n\n' + self._frag_saved_filter()
        result = self.call_GQL(query, {'mode':mode})
        result = result['findSavedFilters']
        if default:
            flt = self.find_default_filter(mode=mode)
            result.insert(0, flt)
        return result

def block_for_job(job_id, status='FINISHED', label=None):
    return asyncio.run(await_job(job_id, status=status, label=label))

async def await_job(job_id, status='FINISHED', label=None):
    if label:
        label = f'Job {job_id}: {label}' if status == 'FINISHED' else f'Job {job_id} {status}: {label}'
    else:
        label = f'Job: {job_id}' if status == 'FINISHED' else f'Job {job_id}: {status}'

    while True:
        #print(f'  Await {label}')
        job = API.find_job(job_id)
        if not job:
            raise Exception(f'No such Stash job: {repr(job_id)}')

        if job['status'] == status:
            return True

        if job['status'] in ['FINISHED', 'CANCELLED']:
            log.warning(f'WARN: Job {job_id} status expected {repr(status)} got: {repr(job["status"])}')
            return False # Not what the caller wanted.

        # Wait to try again
        await asyncio.sleep(2)

def studio_has_tag(studio, *needed_tag_names):
    tags = studio['tags']
    return is_in_tags(tags, *needed_tag_names)

def performer_has_tag(performer, *needed_tag_names):
    tags = performer['tags']
    return is_in_tags(tags, *needed_tag_names)

def scene_has_tag(scene, *needed_tag_names):
    tags = scene['tags']
    return is_in_tags(tags, *needed_tag_names)

def is_in_tags(tags, *needed_tag_names):
    missing = get_missing_tags(tags, *needed_tag_names)
    return not missing

def get_missing_tags(tags, *needed_tag_names):
    if not isinstance(tags, list):
        raise ValueError(f'Tags must be a list of tag objects: {repr(tags)}')
    if not all(isinstance(X, dict) for X in tags):
        raise ValueError(f'Tag objects must be dictionaries: {repr(tags)}')
    if not all(X.get('name') for X in tags):
        raise ValueError(f'Tags must have "name" attributes: {repr(tags)}')

    missing = []
    current_tag_names = [ X['name'] for X in tags ]
    for needed_tag_name in needed_tag_names:
        if needed_tag_name not in current_tag_names:
            missing.append(needed_tag_name)
    return missing

def scan_flags():
    scan_flags = {}
    for suffix in ['ClipPreviews', 'Covers', 'ImagePreviews', 'Phashes', 'Previews', 'Sprites', 'Thumbnails']:
        gen_flag = 'scanGenerate' + suffix
        scan_flags[gen_flag] = False
    return scan_flags

def main():
    log.info(f'ok')

if __name__ == '__main__':
    main()
