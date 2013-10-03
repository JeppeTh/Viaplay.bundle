Viaplay Plex Plugin
====================

Provides access to the content available from Viaplay.

NOTE!!!
Password is visible in and/or
...\Plex Media Server\Logs\PMS Plugin Logs\com.plexapp.plugins.viaplay.log
...\Plex Media Server\Logs\PMS Plugin Logs\com.plexapp.system.log
NOTE!!!

# Installation

With Git (Recommended):

    $ cd ~/Library/Application Support/Plex Media Server/Plug-ins/
    $ git clone git://github.com/hitolaus/Viaplay.bundle.git

With Zip (Only if Git scares you): 
Download the ZIP and extract it:

    $ curl -k -L https://github.com/hitolaus/Viaplay.bundle/zipball/master > /tmp/viaplay.zip
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
03/10/2013:
+ Made it work again
+ Added Search function
+ Added Sport Category
+ Added User Logon
+ Added Season support amongst TV Shows

22/11/2012:
+ Added iOS support

15/09/2012:
+ First usable version
