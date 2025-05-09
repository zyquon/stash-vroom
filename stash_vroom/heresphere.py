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

Example
-------

Here's a basic example of using the HereSphere API:

.. code-block:: python

    from stash_vroom.heresphere import on_event

    @on_event('play')
    def on_play(scene):
        print(f"Playing scene: {scene.title}")

    @on_event('favorite')
    def on_favorite(scene):
        print(f"Marking scene as favorite: {scene.title}")

    @on_event('un-favorite')
    def on_unfavorite(scene):
        print(f"Marking scene as not favorite: {scene.title}")

"""

import logging
from typing import Callable, Dict, List, Optional, Any

log = logging.getLogger(__name__)

class Scene:
    """
    Represents a video scene in HereSphere.
    
    This is a simplified representation that will be passed to event handlers.
    """
    
    def __init__(self, id: str, title: str, path: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a Scene object.
        
        :param id: Unique identifier for the scene
        :param title: Title of the scene
        :param path: File path to the scene
        :param metadata: Optional dictionary of additional metadata
        """
        self.id = id
        self.title = title
        self.path = path
        self.metadata = metadata or {}
    
    def __str__(self) -> str:
        return f"Scene({self.id}, {self.title})"
    
    def __repr__(self) -> str:
        return self.__str__()

class HereSphereApp:
    """
    Main class for the HereSphere application.
    
    Similar to Flask's Flask class, this manages event handlers and provides
    decorators for registering them.
    """
    
    def __init__(self, name: str):
        """
        Initialize a HereSphereApp.
        
        :param name: Name of the application
        """
        self.name = name
        self.event_handlers: Dict[str, List[Callable[[Scene], Any]]] = {}
        log.info(f"Initialized HereSphereApp: {name}")
    
    def on_event(self, event_name: str):
        """
        Decorator for registering event handlers.
        
        :param event_name: Name of the event to handle (e.g., "delete", "favorite", "play")
        :return: Decorator function
        """
        def decorator(func: Callable[[Scene], Any]):
            if event_name not in self.event_handlers:
                self.event_handlers[event_name] = []
            self.event_handlers[event_name].append(func)
            log.debug(f"Registered handler for event {event_name}: {func.__name__}")
            return func
        return decorator
    
    def trigger_event(self, event_name: str, scene: Scene) -> List[Any]:
        """
        Trigger an event and call all registered handlers.
        
        :param event_name: Name of the event to trigger
        :param scene: Scene object to pass to handlers
        :return: List of results from all handlers
        """
        results = []
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                log.debug(f"Calling handler {handler.__name__} for event {event_name}")
                try:
                    result = handler(scene)
                    results.append(result)
                except Exception as e:
                    log.error(f"Error in handler {handler.__name__}: {e}")
        else:
            log.warning(f"No handlers registered for event {event_name}")
        return results

# Create a global app instance for convenience
app = HereSphereApp("default")

# Convenience functions that use the global app
def on_event(event_name: str):
    """
    Decorator for registering event handlers on the global app.
    
    :param event_name: Name of the event to handle
    :return: Decorator function
    """
    return app.on_event(event_name)

def trigger_event(event_name: str, scene: Scene) -> List[Any]:
    """
    Trigger an event on the global app.
    
    :param event_name: Name of the event to trigger
    :param scene: Scene object to pass to handlers
    :return: List of results from all handlers
    """
    return app.trigger_event(event_name, scene)