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
This module provides a convenient way to serve Stash content to HereSphere
and easily handle user events and interactions without writing an entire web service.
"""

import io
import re
import copy as Copy
import math
import logging
import threading
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from typing import Dict, List, Callable, Any, Optional
from flask import ( Flask, g, request, Response, jsonify, make_response )

from . import util
from . import stash
from . import changes

log = logging.getLogger(__name__)

class HereSphere(Flask):
    """
    Main class for the HereSphere application.
    
    Similar to Flask's Flask class, this manages event handlers and provides
    decorators for registering them.
    """
    
    def __init__(self, name='Stash VRoom HereSphere Service', **kwargs):
        """
        Initialize a VRoom HereSphere web service.
        
        :param name: Name of the application
        :param stash_hostname: Hostname of the Stash server
        :param kwargs: Additional keyword arguments for Flask
        """
        super().__init__(name, **kwargs)
        self._vroom_lock = threading.Lock()

        self._vroom_stash = None # Will be initialized later with init_stash()

        self._vroom_cache = {}
        self._vroom_state = {}
        self._vroom_state['last_query_at'] = None # datetime.datetime.now()
        self._vroom_state['inputs'] = {} # scene_id -> [ (timestamp, str), (timestamp, str), ...]
        self._vroom_state['doubleclick'] = {} # scene_id -> timestamp
        self._vroom_state['playback'] = {} # scene_id -> timestamp

        self._vroom_handlers = {}
        self._vroom_handlers['_cheats'] = {} # directions tuple -> list of handlers

        self._vroom_views = []
        # self._vroom_changes = changes.SceneChanges(stash_api=self._vroom_stash)
        # self._vroom_changes.on('insert_view', self._insert_view)
        # self._vroom_changes.on('delete_view', self._delete_view)
        # self._vroom_changes.on('insert_scene', self._insert_scene)
        # self._vroom_changes.on('delete_scene', self._delete_scene)
        self._register_routes()
        log.info(f"Initialized VRoom app: {name}")

        # log.debug(f'Start changes feed')
        # self._vroom_changes.start()
    
    def init_stash(self, stash_url, stash_headers=None, validate=True):
        # Initialize the Stash connection. This runs just before the Flask app runs.
        self._vroom_stash = stash.init(stash_url=stash_url, stash_headers=stash_headers, validate=validate)
    
    def _cache_set(self, key: str, value: Any):
        with self._vroom_lock:
            self._vroom_cache[key] = value
        return value
        
    def _cache_get(self, key, copy=False) -> Optional[Any]:
        with self._vroom_lock:
            val = self._vroom_cache.get(key)
        if copy:
            val = Copy.deepcopy(val)
        return val
    
    def _insert_view(self, view_name, scene_ids):
        log.debug(f"Insert view: {view_name}")
        log.debug(f'- Scene IDs: {len(scene_ids)}')
    
    def _delete_view(self, view_name):
        log.debug(f"Delete view: {view_name}")
    
    def _insert_scene(self, scene, view_name, position):
        log.debug(f"Insert scene: {scene['id']} into view: {view_name} at position: {position}")
    
    def _delete_scene(self, scene_id, view_name, position):
        log.debug(f"Delete scene: {scene_id} from view: {view_name}")

    def _register_routes(self):
        """Register Flask routes to handle various events."""
        
        # Root endpoint for app info
        @self.route('/')
        def index():
            response = make_response('<h1>Go to the <a href="heresphere">VRoom HereSphere UI</a></h1>', {'content-type':'text/html'})
            # 'Press this button - - - ^</h2>', {'content-type':'text/html'}
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        
        @self.route('/heresphere', methods=['GET', 'POST'])
        def heresphere():
            if request.method == 'GET' and 'HereSphere-JSON-Version' not in request.headers:
                return f'<h2>Press this button - - - ^</h2>', {'content-type':'text/html'}

            body = {'access': 1}

            body['banner'] = {}
            body['banner']['image'] = self._get_hs_url('/legend')
            #body['banner']['link'] = 'http://www.example.com'

            if request.method == 'POST' and request.form and request.form['login']:
                log.debug(f'Login: {repr(request.form)}')
                #body['authorized'] = '1'

            body['library'] = self._cache_get('library') or []
            for lib in body['library']:
                for i, url in enumerate(lib['list']):
                    if not url.startswith('http'):
                        lib['list'][i] = request.url_root + url
            return jsonify(body), {'HereSphere-JSON-Version': 1}

        @self.route('/heresphere/legend', methods=['GET'])
        def heresphere_legend():
            img_width, img_height = (1920, 200)
            shortcuts = self._get_hs_shortcuts()

            #num_cols = 3
            #num_rows = math.ceil(len(shortcuts) / num_cols) # Buggy
            num_rows = 7
            num_cols = math.ceil(len(shortcuts) / num_rows)
            log.debug(f'Legend content size: {len(shortcuts)} shortcuts as {num_cols} cols x {num_rows} rows')

            img = PIL.Image.new("RGB", (img_width, img_height), color="white")
            draw = PIL.ImageDraw.Draw(img)

            font_mono = util.get_font_dirpath() + '/VeraMono.ttf'
            log.debug(f'Font: {font_mono}')
            font = PIL.ImageFont.truetype(font_mono, 24)

            cell_width = img_width / num_cols
            cell_height = img_height / num_rows

            padding_x = 10
            padding_y = 1

            actions = []
            for _id, dirs, description in shortcuts:
                dirs = util.split_comma(dirs)
                dirs = [ X[0] for X in dirs ]
                while len(dirs) < 6:
                    dirs.insert(0, ' ')
                dirs = ' '.join(dirs)
                actions.append({'dirs':dirs, 'description':description})

            for i, action in enumerate(actions):
                dirs = action['dirs']
                description = action['description']

                # Row-oriented
                #col = i % num_cols
                #row = i // num_cols

                # Column-oriented
                row = i % num_rows
                col = i // num_rows

                # Top-left corner of this "cell"
                x = col * cell_width + padding_x
                y = row * cell_height + padding_y

                text = f'{dirs} | {description}'
                draw.text((x, y), text, font=font, fill="black")

            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            return Response(img_bytes, mimetype="image/png")
    
    def _handle_event(self, event_name: str, scene_id: str) -> Response:
        """
        Handle an event from HereSphere.
        
        :param event_name: Name of the event
        :param scene_id: ID of the scene
        :return: Flask response
        """
        log.info(f"Handling event: {event_name} for scene: {scene_id}")
        
        # Check if we have handlers for this event
        handlers = self._vroom_handlers.get(event_name, [])
        if not handlers:
            log.warning(f"No handlers for event: {event_name}")
            return jsonify({"status": "no_handler", "event": event_name}), 200
        
        # Call all handlers for this event
        results = []
        for handler in handlers:
            try:
                result = handler(scene_id)
                results.append({
                    "handler": handler.__name__,
                    "result": str(result) if result is not None else None
                })
            except Exception as e:
                log.error(f"Error in handler {handler.__name__}: {e}")
                results.append({
                    "handler": handler.__name__,
                    "error": str(e)
                })
        
        return jsonify({
            "status": "ok",
            "event": event_name,
            "scene_id": scene_id,
            "results": results
        })
    
    def on_doubleclick(self):
        return self._on('doubleclick')
    
    def cheatcode(self, name, *args):
        """
        Register a cheat code.
        
        :param name: Name of the cheat code
        :param args: D-Pad directions: "up", "down", "left", "right"
        :return: Decorator function
        """

        if not name or not isinstance(name, str):
            raise ValueError(f"Invalid cheat code name: {repr(name)}")

        directions = []
        for arg in args:
            arg = arg.lower()
            if arg not in ['up', 'down', 'left', 'right']:
                raise ValueError(f"Invalid direction: {arg}")
            directions.append(arg)
        
        cheat_id = tuple(directions)
        if cheat_id in self._vroom_handlers['_cheats']:
            existing_cheat_name = self._vroom_handlers['_cheats'][cheat_id]
            raise ValueError(f"Cheat code {cheat_id} already registered as {existing_cheat_name}")

        def decorator(func: Callable[[str], Any]):
            self._vroom_handlers['_cheats'][cheat_id] = func
            log.debug(f"Registered cheat code {name}: {func.__name__}")
            return func
        return decorator

    def _on(self, event_name: str):
        """
        Decorator for registering event handlers.
        
        :param event_name: Name of the event to handle (e.g., "delete", "favorite", "play")
        :return: Decorator function
        """

        if not event_name or event_name[0] == '_':
            raise ValueError(f"Invalid event name: {event_name}")

        def decorator(func: Callable[[str], Any]):
            if event_name not in self._vroom_handlers:
                self._vroom_handlers[event_name] = []
            self._vroom_handlers[event_name].append(func)
            log.debug(f"Registered handler for event {event_name}: {func.__name__}")
            return func
        return decorator

    def _get_hs_url(self, path):
        path = re.sub(r'^/', '', path)
        return self._get_server_url() + '/heresphere/' + path

    def _get_server_url(self):
        url = f'http://{stash.STASH_IP}:5000' # Always use the IP address as HereSphere needs it.
        url = self._get_normal_url(url) # In case the STASH_IP is a hostname somehow.
        return url
    
    def _get_normal_url(self, url):
        #url = re.sub(r'169\.254\.\d+\.\d+', stash.STASH_IP, url)
        url = url.replace(stash.STASH_HOST, stash.STASH_IP) # Because Meta Quest 3 does not have Bonjour/Rendezvous.
        return url
    
    def run(self, stash_url, stash_headers, host='0.0.0.0', **kwargs):
        """
        Run the VRoom HereSphere service.
        
        :param stash_url: URL of the Stash server
        :param stash_headers: Headers to use for Stash API requests
        :param host: Hostname to bind to
        :param kwargs: Additional options for Flask
        """
        log.debug(f"Run VRoom app on host: {repr(host)}")
        self.init_stash(stash_url, stash_headers)
        super().run(host=host, **kwargs)