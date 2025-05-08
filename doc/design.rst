Design and Internals
====================

This section explains the design, tradeoffs, and internal thinking behind the project.

.. contents::
   :local:

Philosophy
----------

- VR on Stash should be very easy
- HereSphere on Stash should be as convenient and intuitive as possible.
- VRoom should be useful for developers to build advanced HereSphere functionality.

To make VR on Stash easy, VRoom will be a Stash plugin, easy to install. It aspires to be
a reliable, mature tool providing all the services needed to manage VR Stash content. (If it is truly
easy, the plugin may need to display a link to paste to HereSphere or something, instead of asking
the user to figure out their hostname and URL.)

To make the HereSphere experience convenient and intuitive, VRoom has no UI and minimal configuration.
VRoom should be transparent. HereSphere should just be a nice new way to browse our Stash we know and love.
To change what see in HereSphere, change your data in Stash. VRoom makes HereSphere reflect your Stash content directly:
- Stash **Saved Filters** become HereSphere **Libraries**. To see VR scenes in HereSphere, just make a Filter called ``VR``. You will recognize the Filter view in HereSphere.
- Scene **Tags** become HereSphere **Tags**. You can browse them in HereSphere, and click to filter scenes by tag.
- Scene **Markers** become HereSphere **Tags** also. (Yes, HereSphere reuses tags for this.) VRoom makes it right. You can search, jump, and autoseek to any marker. If you make VRoom read-write, as you add and edit HereSphere tags, they are saved as Stash scene markers. (This can be very fast and powerful.)
- Performers become HereSphere **Tags** as a ``Performer`` dropdown. You can browse performers by name, and click to filter by performer.
- Scene **Star Rating** appears in HereSphere. If you make VRoom read-write, click a star rating in HereSphere to update the star rating in Stash.

To be useful for developers, VRoom has two parts:
1. A ready-to-go Stash plugin that does all of the above.
2. A developer library for easy building of a different tool servicing HereSphere using Stash. ``stash_vroom`` connects it all and
   gives you convenient helpers and event triggers. But you completely control what to send to HereSphere and how to query Stash.

Tradeoffs
---------

- Performance vs. readability.
- Flexibility vs. simplicity.

Internals
---------

- Explanation of core modules like `slr.py`.
- How regex patterns are used for filename parsing.

.. Here is an example of the `say_hello` function:

.. .. literalinclude:: ../stash_vroom/jav.py
      :language: python
      :lines: 14-20