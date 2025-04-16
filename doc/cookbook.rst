Cookbook
========

This section provides practical examples and recipes for using the library.

.. contents::
   :local:

Example 1: Detecting SLR Files
------------------------------

To do

Example 2: Handling HereSphere Events
-------------------------------------

This example shows how to use the HereSphere API to handle UI events:

.. code-block:: python

    from stash_vroom.heresphere import on_event, trigger_event, Scene
    
    # Define event handlers
    @on_event('play')
    def on_play(scene):
        print(f"Playing scene: {scene.title}")
        return True
    
    @on_event('favorite')
    def on_favorite(scene):
        print(f"Marking scene as favorite: {scene.title}")
        scene.metadata['favorite'] = True
        return scene.metadata
    
    @on_event('delete')
    def on_delete(scene):
        print(f"Deleting scene: {scene.title}")
        # In a real implementation, you would delete the file
        return True
    
    # Test the handlers
    test_scene = Scene(
        id="123",
        title="Test Scene",
        path="/path/to/test.mp4",
        metadata={"studio": "Test Studio"}
    )
    
    # Trigger events
    trigger_event('play', test_scene)
    trigger_event('favorite', test_scene)
    trigger_event('delete', test_scene)