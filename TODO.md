Bugs
====

Foo

Features
========

1. Serving images to HS by maybe streaming or creating a temporary video file with ffmpeg
1. If it is truly easy, the plugin may need to display a link for them to click or paste to HereSphere or something, instead of asking the user to figure out their hostname and URL. Maybe it's a page with
    1. Instructions about what's about to happen
        - this link will change your HereSphere browser into VR video mode...
        - If it works, **bookmark that location**. If you bookmark successfully, you should see the URL in the "Web" section of HereSphere's Main Menu.
        - (Possible to detect the HS user-agent from a Stash UI plugin? From JS? Confirm or warn the user in the Stash UI)
    1. The link to the HS URL
    1. Maybe common pitfalls or errors, troubleshooting
        1. The URL has a `.local` host name (Quest 3 cannot do `.local` LAN)
        1. Host not found
        1. Connection refused
        1. It says *Click here for VRoom*