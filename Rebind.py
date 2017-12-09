# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 22:14:44 2017

@author: Robert
"""

print("Remapping keys.")
with open("bindings.txt", 'r+') as f:
    bindings = [l.replace("\n", "") for l in f.readlines()]
    
    done = False
    while not done:
        to_bind = input("key/option to set/bind?  (Thrust, Brake, Left, Right, Mousemode, Photon, Missile, or Exit). 'Quit' to quit, 'Default' to restore to defaults  ")
        if to_bind.lower() == "thrust":
            new = input("Bind Thrust to?  (currently '" + bindings[0] + "')  ")
            bindings[0] = new
            print ("Bound 'Thrust' to '" + new + "'")
        elif to_bind.lower() == 'brake':
            new = input("Bind Brake to?  (currently '" + bindings[1] + "')  ")
            bindings[1] = new
            print ("Bound 'Brake' to '" + new + "'")
        elif to_bind.lower() == 'left':
            new = input("Bind Left to?  (currently '" + bindings[2] + "')  ")
            bindings[2] = new
            print ("Bound 'Left' to '" + new + "'")
        elif to_bind.lower() == 'right':
            new = input("Bind Right to?  (currently '" + bindings[3] + "')  ")
            bindings[3] = new
            print ("Bound 'Right' to '" + new + "'")
        elif to_bind.lower() == 'mousemode':
            new = input("Set Mousemode to?  (currently '" + bindings[4] + "') (Must be True or False)  ")
            if new.lower() == "true" or new.lower() == "false":
                bindings[4] = "True" if new == "True" else "False"
                print ("Bound 'Mousemode' to '" + new + "'")
            else:
                print("Mousemode must be either True or False")
        elif to_bind.lower() == 'photon':
            new = input("Bind Photon to?  (currently '" + bindings[5] + "')  ")
            bindings[5] = new
            print ("Bound 'Photon' to '" + new + "'")
        elif to_bind.lower() == 'missile':
            new = input("Bind Missile to?  (currently '" + bindings[6] + "')  ")
            bindings[6] = new
            print ("Bound 'Missile' to '" + new + "'")
        elif to_bind.lower() == 'exit':
            new = input("Bind Exit to?  (currently '" + bindings[7] + "')  ")
            bindings[7] = new
            print("Bound 'Exit' to '" + new + "'")
        elif to_bind.lower() == 'quit':
            done = True
            print("quitting")
        elif to_bind.lower() == 'default':
            with open("default_bindings.txt", 'r') as g:
                bindings = [l.replace("\n", "") for l in g.readlines()]
            print("Keys reset to defaults")
        else:
            print("Unrecognized input.  Try again.  ")
        print("")
    f.seek(0)
    for l in bindings:
        f.write(l + "\n")