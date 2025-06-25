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

# TODO: https://github.com/pyapp-kit/psygnal?tab=readme-ov-file#evented-containers

import re
import logging
import psygnal
from typing import Callable, Dict, List

log = logging.getLogger(__name__)

class SceneChanges:
    """
    A class for managing scene-related events using psygnal.
    """

    # Define signals for events
    insert_view = psygnal.Signal(object)  # Signal with a single argument (e.g., a view object)
    delete_view = psygnal.Signal(object)
    insert_scene = psygnal.Signal(object)
    delete_scene = psygnal.Signal(object)

    def __init__(self, stash_api, blacklist=None):
        self.stash = stash_api
        self.blacklist = blacklist or []

        self.views = []
        self.scenes = {}
        log.info("Initialized SceneChanges")

    def start(self):
        """
        Start the SceneChanges event manager.
        """
        log.info("Start SceneChanges")
        self.boot_scenes()

    def boot_scenes(self):
        """
        Load scenes and views, emitting signals for each event.
        """
        scene_filters = self.stash.find_saved_filters(mode='SCENES')
        log.debug(f'Scene filters found: {len(scene_filters)}')

        for flt in scene_filters:
            if flt['name'] in self.blacklist:
                log.debug(f'Skip blacklisted filter: {flt["name"]}')
                continue

            # Example: Emit an insert_view signal
            self.insert_view.emit(flt)
            log.debug(f'Emitted insert_view for filter: {flt["name"]}')