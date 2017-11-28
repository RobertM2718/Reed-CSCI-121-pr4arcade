# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 21:24:31 2017

@author: Robert
"""
#???? Make this script into an object, to make building an actual menu easier and to allow the user to quit in the middle of setting up a host/client?  
import Host
import Client
import time

#c = Client.Client("hi", 60, 45, 800, 600, 'wrapped', 0)
#h = Host.Host("No", 60, 45, 800, 600, 'wrapped', 0)
#
#h.add_connection(c)
#c.set_host(h)



#c.add(Game.Agent(Point2D(100, 100), c, "7AB")) #I got an error where many windows were opened.  What?  
#error doesn't seem to be critical.  

while True:
    h_or_c = input("Host or Client?  ")
    if h_or_c == "host" or h_or_c == "Host":
#        default_address = socket.gethostbyname(socket.gethostname())
#        address = input("Address?  (probably best to stick with 'localhost'  ")
#        while True:
#            address = input(("Address to host on?  ")) #I can't just ask the player for a valid address.  I need to find a way to get the computer's address.  
#            if len(address.split(".")) < 4 or len(address.split(".")) > 5:
#                print("Invalid IP address.  Try again.")
#            else:
#                break
#        while True:
#            l_or_p = input(("Local or Public?  ")) #I can't just ask the player for a valid address.  I need to find a way to get the computer's address.  
#            if len(address.split(".")) < 4 or len(address.split(".")) > 5:
#                print("Invalid IP address.  Try again.")
#            else:
#                break
        while True:
            try:
                port = int(input("Port number?  (probably 10000)  "))
            except ValueError:
                print("Port must be an integer.  Try again.")
                continue #will this work?  Yes!
            break
#        address = ('localhost', port) #does the first part of address need to be determined after the socket is made?  Probably.  
        while True:
            try:
                num_cns = int(input("Number of players?  (probably at least 1)  "))
            except ValueError:
                print("Number of players must be an integer.  Try again.")
                continue #will this work?
            break
        print ("Initializing Host")
        h = Host.Host("No", 60, 45, 800, 600, 'wrapped', 0, port, num_cns) #I think the issue I was having was leaving out console_lines(the 0)
        while not h.GAME_OVER:
            time.sleep(1.0/60)
            h.update()
    elif h_or_c == "client" or h_or_c == "Client":
        c = Client.Client("Asteroids Arena", 60, 45, 800, 600, 'wrapped', 0)
        #???? There needs to be some way of verifying that a proper connection was formed.  
        #Note: there sort of is: I could use try/except with a ConnectionRefusedError.  Maybe a few other errors, too.  
#        address = input("Host address?  Example: 'localhost'  ") #example may need to be changed
        while True:
            while True:
                address = input("Host IP address?  ")
                if len(address.split(".")) < 4 or len(address.split(".")) > 5:
                    print("Invalid address.  Try again.")
                else:
                    break
                
            while True:
                try:
                    port = int(input("Port number?  (probably 10000)  "))
                except ValueError:
                    print("Port must be an integer.  Try again.")
                    continue #will this work?  Yes!
                break
            try:
                c.set_host((address, port))
            except ConnectionRefusedError:
                print("Connection failed.  Try again.")
                continue
            break #should I be consistent in how I get out of these loops?
        while not c.GAME_OVER: 
            c.update()
#        new_test = input("This is a test, please work (also, press enter to close)") #Didn't work - it kept freezing the program.  
#        while not c.GAME_OVER:
#            time.sleep(1.0/60) #this could cause problems; I'm just trying to make sure that the Client version of Main doesn't break Host.      
    else: #Seems to have the consequence of freezing host.  How else can I do this?  Can I set Client in its own update loop, and make it so that instead of drawing instantly on handle_input, it updates a 'to_draw' string?  
        print("Unrecognized type.  Try again.")
        print()
        continue
    break
    #Maybe it's that the Client version of Main terminates too early?  Is that it?  

print("shutting down") #test - so it seems client DOES shut down normally, which causes the problem w/ host.  