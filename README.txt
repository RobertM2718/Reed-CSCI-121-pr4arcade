CONTENTS OF FOLDER:

bindings.txt: A text file which stores the key-bindings Client uses to interpret user input.  

Client.py: A file which stores the Client class, which controls the window that displays the game state to the player and deals with their input, and which transmits that input to a Host instance.  

default_bindings.txt: A text file which stores the default key-bindings, so that they can be restored.  

Game.py: This is the same Game.py as was in the downloadable starter code.  

geometry.py: Again, same geometry.py as in the starter code.  

Host.py: A file which stores the Host class, which takes input from Client instances, runs the game, and tells the Clients what to draw.  

IMPROVEMENTS.txt: A file which contains the results of me desperately begging for points.  Please!  Mercy!  

Main.py: The star of the show.  Running this file creates a Host or a Client, which lets you play the game.  

PlayAsteroids.py: A file which contains all of the objects used in the game.  It's a heavily modified version of the file of the same name within the downloadable starter code.  

README.txt: This file.  Unless YOU changed it.  

Rebind.py: A script which allows the user to rebind their keys.  I couldn't figure out how to run it within Main.py, so it has to be run seperately.  



DESCRIPTION OF GAME:

	This game is a multiplayer version of Asteroids.  Ships spawn in the middle of the screen, all on top of one another, with their weapons disabled until asteroids start spawning.  
	The goal of the game is pretty simple - be the last one standing.  

	The default controls/settings are: 'w' to thrust, 's' to brake, 'a' to turn counterclockwise, 'd' to turn clockwise, MOUSEMODE on, 'u' to fire photons, 'i' to fire missiles, and 'p' to quit (Just so it isn't near the thrust key).  Thrusting moves your ship forward, braking slows it down (regardless of facing), turning (of course) turns it, firing fires the appropriate projectile, and quitting closes the window and exits the game.  
	When MOUSEMODE is on, the two firing keys are ignored, and the ship fires based on the mouse - photons on a left-click, missiles on a right-click.  It fires towards the mouse's position (indicated by some pretty sharp rotating triangles).  
	When MOUSEMODE is off, the ship fires straight ahead of it whenever one of the firing keys is pressed.  Unfortunately, due to budgetary shortfalls, firing missiles doesn't really work  when MOUSEMODE is off - they mostly sort of hang out in front of your ship.  Also, the cursor thingy shows up even if MOUSEMODE is off.  



INSTRUCTIONS:

	In order to play the game in Multiplayer mode, one person runs "Main.py" and sets up a host, following the prompts.  Then, each person playing opens a fresh command prompt, and runs "Main.py" to make themselves clients, again following the prompts.  Once all clients have connected, the game should begin automatically.  

	In order to play the game in singleplayer mode, open two command prompts.  Set up a host in one of them, and a client in the other.  The 'default' and 'localhost' inputs to Main (when asked for) will speed the process up, but you should be able to connect in the same way you connect in a multiplayer game.  

	When creating a host, enter "host" (or "HOST", or "HoSt", it should ignore capitalization).  Then, enter the port you'd like to host on, and the number of players who will be playing.  Alternatively, enter 'default' when asked for a port to host on Port 10000 for 1 player.  

	When creating a client, enter "client".  Then, enter the host's IP address, followed by the host's port.  Alternatively, enter 'localhost' when asked for an IP address to connect to the local host on port 10000.  

	In order to remap your keys, and set whether firing missiles and photons is controlled by the keyboard or the mouse, run "Rebind.py" and follow the prompts.  This will work just fine while the game is running, but it won't have an effect unless the game is restarted.  