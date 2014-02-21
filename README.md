Viaplay Plex Plugin
====================

Provides access to the content available from Viaplay.

# Installation

With Git (Recommended):

    $ cd ~/Library/Application Support/Plex Media Server/Plug-ins/
    $ git clone git://github.com/JeppeTh/Viaplay.bundle.git

With Zip (Only if Git scares you): 
Download the ZIP and extract it:

    $ curl -k -L https://github.com/JeppeTh/Viaplay.bundle/zipball/master > /tmp/viaplay.zip
    $ cd ~/Library/Application Support/Plex Media Server/Plug-ins/
    $ unzip /tmp/viaplay.zip

Now Plex should see the Viaplay plugin.

# Compatibility

Tested to work on the following clients:

- Mac
- Windows
- Roku 
- iOS

Does *NOT* work on the following clients:

- LG MediaLink

# Credits

This project makes use of the following external dependencies:

- Metro UI Dock Icon Set <a href="http://dakirby309.deviantart.com/gallery/#/d4n4w3q">http://dakirby309.deviantart.com/gallery/#/d4n4w3q</a>

# Changes
22/02/2014:
+ Remove hardcoded url for fetching stream (may require PIN to be added in config)
+ Fixed search for Samsung Plex
+ Added support for PIN (no pop-up though).

12/02/2014:
+ Fixed bug which made it impossible to run plugin at initial installation.

08/02/2014:
+ Also streaming should be working - thx wouterdebie!

06/02/2014:
+ Major changes to adapt to the new viaplay
+ Only browsing works in this version.

03/10/2013:
+ Made it work again
+ Added Search function
+ Added Sport Category
+ Added User Logon
+ Added Season support amongst TV Shows
+ Added Finland support

22/11/2012:
+ Added iOS support

15/09/2012:
+ First usable version
