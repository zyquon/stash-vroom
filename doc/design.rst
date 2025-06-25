Design and Internals
====================

This section explains the design, tradeoffs, and internal thinking behind the project.

.. contents::
   :local:

Philosophy
----------

- VR on Stash should be easy, fun, and rewarding
- Browsing VR Stash content with HereSphere should be easy and intuitive
- Help everyday users browse their VR Stash, and also help developers build similar technology

To make VR on Stash easy, **VRoom is a Stash plugin**: easy to install, easy to run, easy to configure.
VRoom aspires to be a reliable, mature tool providing all the services needed to
manage VR Stash content.

To make the HereSphere experience convenient and intuitive, VRoom has no UI and minimal configuration.
VRoom should be transparent. HereSphere should just be a nice new way to browse our Stash we know and love.
To change what you see in HereSphere, change your data in Stash. VRoom makes HereSphere reflect your Stash content directly:
- Stash **Saved Filters** become HereSphere **Libraries**. To see VR scenes in HereSphere, just make a Filter called ``VR``. You will recognize the Filter view in HereSphere.
- Scene **Tags** become HereSphere **Tags**. You can browse them in HereSphere, and click to filter scenes by tag.
- Scene **Markers** become HereSphere **Tags** also. (Yes, HereSphere reuses tags for this.) VRoom makes it right. You can search, jump, and autoseek to any marker. If you make VRoom read-write, as you add and edit HereSphere tags, they are saved as Stash scene markers. (This can be very fast and powerful.)
- Performers become HereSphere **Tags** as a ``Performer`` dropdown. You can browse performers by name, and click to filter by performer.
- Scene **Star Rating** appears in HereSphere. If you make VRoom read-write, click a star rating in HereSphere to update the star rating in Stash.

To be useful for developers, VRoom has two parts:
1. A plug-and-play Stash plugin that does all of the above.
2. A lower-level Python library to support HereSphere's native video client, using your own logic
   and content with a few lines of code (presumably Stash as a back-end). Rather than coding web handlers,
   you decorate your functions to trigger during HereSphere usage: `on_play`, `on_pause`, `on_stars(3)`, `on_delete`, etc.
   You control the content to send to HereSphere using `your own behavior and content <cookbook.html>`_.

Internals
---------

- Explanation of core modules like `slr.py`.
- Foo bar

.. Here is an example of the `say_hello` function:

.. .. literalinclude:: ../stash_vroom/jav.py
      :language: python
      :lines: 14-20