11/21/2017:
	So far, I've been trying to build a host-client distinction into the logic of Asteroids, in preparation for trying to make it work over a network.  I started with this because I realized that it would be much easier to do this restructuring before I made any changes, than afterwards.  

I have made/modified the following files:

Client:
	This class is supposed to control the window which displays the game, and is supposed to pass the player's inputs to the host.  I built it based on Game, and like Game it inherits from Frame.  
	
Host:
	This class is supposed to contain the game logic, and pass the results of each game tick to the client.  It is based on the original PlayAsteroids class, but it inherits from nothing.  

Main:
	This is (for now) a testing file, which tries to combine Client and Host into a functioning game.  

PlayAsteroids:
	I've added some methods to the classes here in order to help with building the strings that Client and Host pass back and forth.  In addition, I commented out the PlayAsteroids class, as well as the main game loop at the bottom, so that these bits of code don't interfere with what I'm trying to do.  

Currently, running Main causes an error, because Client.handle_input() doesn't acknowledge the fact that different class constructors require different numbers of inputs.  However, I think I'm close to being able to run something close to the starting Asteroids game with a client-host distinction in place.  