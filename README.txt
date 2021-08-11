All wallpapers must end with a '_n', where n is a positive whole number!!!

This app only works for the Windows platform.

Shortcut to backroundChanger.pyw should be placed in Windows Startup folder for it to run on boot.

If you want to use different wallpapers just place/remove necessary wallpapers in the "wallpapers/folderName" folder
and update the relative path in the 'config.json' file, the program does the rest.

backroundChanger.py

Changes the wallpaper depending on the time od day.
No options.


backroundChanger.pyw

Same as backroundChanger.py, but only runs in the backround.


config.json

relativePath - relative/absolute path to the wallpaper set of choice
longitude - longitude of the location of choice
latitude - latitude of location of choice
local - 1 - use fixed set of wallpapers determined by the user
      - 0 - uses the wallpaper sent and chosen by the server


wallpaperServer.py

Chooses, and sends a wallpaper set to the client/s.
No options.


configServe.json

pathToWallpapers - relative/absolute path to the folder containing wallpaper sets


tarrring.py

Contains function for compressing and decompressing wallpaper sets.