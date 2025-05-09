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

Writing your own service to allow browsing and managing Stash from HereSphere,
with your custom logic, is easy and will feel familiar to users of Flask.
Inside HereSphere, it will feel the same as read-only mode. But you can write
handlers for interesting events like the user playing a scene, setting a star rating,
favoriting a scene, etc.

.. code-block:: python

    from stash_vroom.heresphere import HereSphere

    app = HereSphere('My First Service')
    app.run() # Output: "Listening on http://0.0.0.0:5000"

A more interesting example is handling common events from the HereSphere user.

.. code-block:: python

    from stash_vroom.heresphere import HereSphere

    app = HereSphere('My Second Service')
    
    # Define event handlers
    @app.on('play')
    def on_play(scene_id):
        print(f"User is playing scene: {scene_id}")
    
    @app.on('favorite')
    def on_favorite(scene_id):
        print(f"Marking scene as favorite: {scene_id}")
    
    @app.on('delete')
    def on_delete(scene_id):
        # Notice, this function performs no delete.
        # Although HereSphere will remove the scene in its UI, the file remains.
        # Stash data is unchanged. When HereSphere reloads, the scene will reappear.
        print(f"User wishes to delete scene: {scene_id}")

    app.run() # Output: "User is playing scene: 1234", etc.