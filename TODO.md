Bugs
====

1. Document the circumstances and procedure to delete the HS media library and reload
1. Missing events: new tag, unknown tag, star rating, seen, play, pause, doubleclick, fav, unfav
1. Document somewhere a use case for "dynamic" tagging, which is Studio tags, i.e. if a studio has tag X, then tag it Y, which Stash cannot do (except performer tags)

Features
========

1. The ffmpeg wrapper should connect in to Stash and update its parameters for screenshot or preview of SBS or TB VR
1. Maybe a task to "activate" the VR ffmpeg and warn the user this forces the queue size to 1
1. Serving images to HS by maybe streaming or creating a temporary video file with ffmpeg (done in my personal project)
1. If it is truly easy, the plugin may need to display a link for them to click or paste to HereSphere or something, instead of asking the user to figure out their hostname and URL. Maybe it's a page with
    1. Instructions about what's about to happen
        - this link will change your HereSphere browser into VR video mode...
        - If it works, **bookmark that location**. If you bookmark successfully, you should see the URL in the "Web" section of HereSphere's Main Menu.
        - (Possible to detect the HS user-agent from a Stash UI plugin? From JS? Confirm or warn the user in the Stash UI)
        - Isn't there a JS plugin that will link directly to HS somehow? So it's HS already ready to stream a given scene.
    1. The link to the HS URL
    1. Maybe common pitfalls or errors, troubleshooting
        1. The URL has a `.local` host name (Quest 3 cannot do `.local` LAN)
        1. Host not found
        1. Connection refused
        1. It says *Click here for VRoom*