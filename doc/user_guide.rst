User Guide
==========

This section provides a comprehensive guide for using the HereSphere service.

.. contents::
   :local:

How to run VRoom so you can view your VR Stash from HereSphere
---------------------------------------------------------------

Stash-VRoom is not yet implemented as a Stash plugin.

I do not see any plugins that run long-term web services. The theory might be though:

* The plugin exists
* It has a task to start the web service.
* It has a simple config, or maybe just a few tasks to choose from, e.g. read-only mode
* The Stash UI needs a link to the HereSphere service to get the user started. Browse to Stash in HS, then click that link.

TO DO
-----

TODO explain all the current logic out of the box: play/pause, favorite, double click, etc.

Explain "views"
Explain tags vs. markers
Autotagging for e.g. "Peformer:<name>", "
maybe explain or have a footnote or sidebar about how HereSphere tags work and their grouping in the UI

Conveniences

- *Virtual Tags* are computed by VRoom and reported as tags to HereSphere, but not stored in Stash.
  Note, our `philosophy <design.html>`_ is to be transparent and let the hum
   document briefly explains the broad philosophy and goals of Stash-VRoom.
  Because HereSphere uses tags for everything, VRoom makes the Stash world "make sense" and be intuitive in the HereSphere Tags UI.
  (Plus there are a few quality-of-life Virtual Tags.) Below are the major Virtual Tags you will see in HereSphere but not Stash.
   - Scenes tagged for each **Performer**. You can view and filter scenes by performer by selecting the `Performer` dropdown option in HereSphere.
   - Multi-part JAV scenes share a tag grouping them together: `abcdvr-123-part1.foo.mp4` becomes `JAV Title: ABCDVR 123`. If your
      Stash library has JAV, you will see a `JAV Title` dropdown in HereSphere tags.
   - Scenes with no play history tagged ``

Caveats
-------

It's alpha
How delete works (logical delete)

   Local machines with ``.local`` names are convenient on PCs, Macs, and mobile devices.
   Unfortunately, on Quest 3 (at least), HereSphere's web browser cannot use ``.local`` URLs.
   When using HereSphere, use the IP address for the URL, e.g. ``http://192.168.0.<some number>:5000``.

Advanced Mode
-------------

(Still not sure if this is a "mode" of VRoom or maybe a separate plugin?)

- **Marker Surfing** is tons of fun. When marker surfing, VRoom temporarily makes HereSphere use short marker durations
   such as 15 seconds. Now, when you Auto Seek, HereSphere will quickly jump from marker to marker, scene to scene,
   for a fun, hands-off "tour" of the marker genre across all your scenes.
   (Data in Stash remains unchanged.)
   Marker Surfing makes tagging within HereSphere read-only because the incorrect start and end timestamps
   will remain temporarily in HereSphere but not return to the Stash data. (Cheat codes still work while marker surfing.)
- **Cheat Codes** are a method for the HereSphere user to input a sequence of thumbstick directions,
   to trigger helpful server-side actions, often to update Stash information about
   scenes, markers, performers, tags, etc. *Cheat Codes* are hacky but very flexible,
   powerful, and *fast* to work on Stash data without leaving HereSphere.
    
.. important::
   The "banner" at the top of the HereSphere screen will list all cheat codes. To input a cheat code
   in HereSphere, (final warning, it's hacky):
   1. Set your playback speed to 1.0 if it is not already.
   2. Point at the playback speed then hold the secondary trigger. (Now, until you release the trigger, moving the thumbstick will alter the playback speed.))
   3. Input the cheat code sequence on the thumbstick. For example: *Up*, *Right*, *Down*, then *Left*.
   4. Release the trigger. Cheat codes always end back at 1.0 playback speed. You're done. If you made a mistake, click the thumbstick to jump back to 1.0 speed, then start again.