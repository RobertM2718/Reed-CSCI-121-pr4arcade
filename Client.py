# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 14:33:18 2017

@author: Robert
"""
#
#class Client(): #inherit from Game?
#    """
#    Handles input and displays the game state to the user.  
#    """
#    def __init__(self):
#        self.input_data = "{}"
#    
#    def report(self):
#        return self.input_data
#    
#    def receive_game_data(self, data):
#        pass
#    
#    def interpret_game_data(self, data):
#        pass
#    
#    def display(self):
#        pass   


from tkinter import *
from geometry import Bounds, Point2D, Vector2D
import sys   
import Game 
import PlayAsteroids
import socket

class Client(Frame):
    
    def __init__(self, name, w, h, ww, wh, topology = 'wrapped', console_lines = 0):

        # Register the world coordinate and graphics parameters.
        self.WINDOW_WIDTH = ww
        self.WINDOW_HEIGHT = wh
        self.bounds = Bounds(-w/2,-h/2,w/2,h/2)
        self.topology = topology

        # Populate the world with creatures
        self.agents = {}
        self.GAME_OVER = False

        # Initialize the graphics window.
        self.root = Tk()
        self.root.title(name)
        Frame.__init__(self, self.root)
        self.canvas = Canvas(self.root, width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT)

        # Handle mouse pointer motion and keypress events.
        self.mouse_position = Point2D(0.0,0.0)
        self.mouse_down     = False
        self.bind_all('<Motion>',self.handle_mouse_motion)
        self.canvas.bind('<Button-1>',self.handle_mouse_press)
        self.canvas.bind('<ButtonRelease-1>',self.handle_mouse_release)
        self.bind_all('<KeyPress>', self.handle_keypress)
        self.bind_all('<KeyRelease>', self.handle_keyrelease)
        
        #my stuff:
#        self.ship_ID = None #change this later
        #should this report_strings info instead be in Ship?  
        self.report_strings = {"thrust": 0, "spin": 0, "firing_photons": False, "firing_missiles": False}
#        self.create_dict = {"MovingBody": PlayAsteroids.MovingBody, "Shootable": PlayAsteroids.Shootable, 
#                            "Asteroid": PlayAsteroids.Asteroid, "ParentAsteroid": PlayAsteroids.ParentAsteroid,
#                            "Ember": PlayAsteroids.Ember, "ShrapnelAsteroid": PlayAsteroids.ShrapnelAsteroid,
#                            "SmallAsteroid": PlayAsteroids.SmallAsteroid, "MediumAsteroid": PlayAsteroids.MediumAsteroid,
#                            "LargeAsteroid": PlayAsteroids.LargeAsteroid, "Photon": PlayAsteroids.Photon, 
#                            "Ship": PlayAsteroids.Ship}
        self.draw_string = ""

        self.canvas.pack()
        if console_lines > 0:
            self.text = Text(self.root,height=console_lines,bg="#000000",fg="#A0F090",width=115)
            self.text.pack()
        else:
            self.text = None
        self.pack()
        
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        print("init", self.sock) #test
        
    def set_host(self, server_address):
        #network stuff:
        
        # Connect the socket to the port where the server is listening
        print('connecting to {} port {}'.format(*server_address))
        self.sock.connect(server_address)
#        print("set_host", self.sock) #test
        #Do I need to do pass_input() here?  To make sure something's been passed?  
        self.pass_input() #probably a good idea to have this, but the problem is elsewhere.  
#        self.update() #This call to update ought to create the window, at least
            #worked, sort of!  Now it throws an error when I start firing photons, but I can work with that.  
            #The error has to do with exceeding recursion depth.  I'll have to check client for an infinite loop or something.  Or maybe Host?  
#        while not self.GAME_OVER: #Should this loop be inside of Main, for consistency?  
#            self.update()
    def report(self,line=""):
        line += "\n"
        if self.text == None:
            print(line)
        else:
            self.text.insert(END,line)
            self.text.see(END)
            
    def add(self, agent, ID): #both - There's an issue: when agent wants to add itself, it only passes a 'self' parameter.  What can I do about this?   How far-reaching will the effects be if I change that?  
        if ID in self.agents: #this should never happen
            pass
        else:
            self.agents[ID] = agent
            
    def remove(self, ID):
        self.agents.pop(ID, None) #None should be unnecessary
        
    def update(self): #needs to update with the output string from host
        if self.GAME_OVER:
            self.root.destroy()
#        for agent in self.agents:
#            agent.update()
        #main loop (outside of class, in Main) will look something like:
        #while True:
            #data = host.get_data()
            #self.handle_data(data)
            #
        self.clear()
#        for ID in self.agents:
#            agent = self.agents[ID] #there has to be a cleaner way of doing this.  Do I care, though?  
#            self.draw_shape(agent.shape(),agent.color())
        
        to_draw = self.draw_string.split("|")
        del to_draw[0]
        for shape in to_draw:
            vals = shape.split(":")
            color = vals[0]
            points = []
            for i in range(1, len(vals)):
                pair = vals[i].split(",")
                x, y= float(pair[0]), float(pair[1])
                points = points + [Point2D(x, y)]
            self.draw_shape(points, color)
        
        Frame.update(self)
        self.receive_output() #maybe this?  Also, I need to clean up these comments.  
        
    def draw_shape(self, shape, color):
#        print(shape)
#        print(color)
        wh,ww = self.WINDOW_HEIGHT,self.WINDOW_WIDTH
        h = self.bounds.height()
        x = self.bounds.xmin
        y = self.bounds.ymin
        points = [ ((p.x - x)*wh/h, wh - (p.y - y)* wh/h) for p in shape ]
        first_point = points[0]
        points.append(first_point)
        self.canvas.create_polygon(points, fill=color)
#        print("drew a shape")

    def clear(self):
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, self.WINDOW_WIDTH, self.WINDOW_HEIGHT, fill="#000000")

    def window_to_world(self,x,y):
        return self.bounds.point_at(x/self.WINDOW_WIDTH, 1.0-y/self.WINDOW_HEIGHT)
        
    def handle_mouse_motion(self,event): #client
        self.mouse_position = self.window_to_world(event.x,event.y)
        #print("MOUSE MOVED",self.mouse_position,self.mouse_down)

    def handle_mouse_press(self,event): #client
        self.mouse_down = True
        self.handle_mouse_motion(event)
        #print("MOUSE CLICKED",self.mouse_down)

    def handle_mouse_release(self,event): #client
        self.mouse_down = False
        self.handle_mouse_motion(event)
        #print("MOUSE RELEASED",self.mouse_down)

    def handle_keypress(self,event): #both (so the host can quit)
        Game.Game.handle_keypress(self, event)
        
#        self.thrusting = "0" # -1 -> braking, 0 -> neutral, 1 -> thrusting
#        self.rotating = "0" # -1 -> left, 0 -> neutrual, 1 -> right
#        self.energy = "100" # 0-100
#        self.firing_photons = "False"
#        self.photon_cooldown = 0 #ticks till another photon can be launched
#        self.firing_missiles = "False"
#        self.
        if event.char == 'i':
            if self.report_strings["thrust"] < 1: #This style might make things a little awkward.  
                self.report_strings["thrust"] += 1
        elif event.char == 'j':
            if self.report_strings["spin"] < 1:
                self.report_strings["spin"] += 1
        elif event.char == 'l':
            if self.report_strings["spin"] > -1:
                self.report_strings["spin"] -= 1
        elif event.char == ' ':
            self.report_strings["firing_photons"] = True
            
    def handle_keyrelease(self, event):
        if event.char == "i":
            if self.report_strings["thrust"] > -1:
                self.report_strings["thrust"] -= 1
        elif event.char == 'j':
            if self.report_strings["spin"] > -1:
                self.report_strings["spin"] -= 1
        elif event.char == 'l':
            if self.report_strings["spin"] < 1:
                self.report_strings["spin"] += 1
        elif event.char == ' ':
            self.report_strings["firing_photons"] = False
        
        
    
    def receive_output(self):
#        print(data)
#        expected = 16
#        data = b''
#        while True:    
#            this_data = self.sock.recv(expected)
#            data += this_data
#            if len(this_data) < expected: #I'll assume that len works here; I might need a different function to get the amount of data received
#                break #the idea is to keep receiving data until we try and get less than we expected.  
        len_data = int(self.sock.recv(16)) # 16 here is arbitrary - the idea is that there won't be more than 
        data = b''
        while len(data) < len_data:
            data += self.sock.recv(4096) # also arbitrary
        self.handle_output(data.decode('ascii'))
    
#    def receive_ID(self, data):
#        self.ship_ID = data
    
#    def handle_output(self, data): #handles the string passed from Host
#        commands = data.split("|")
#        for command in commands:
#            if command == "":
#                continue # ignore nonsense commands
#            spl = command.split(":")
#            print("spl=", spl)
#            cmd = spl[0]
#            vals = spl[1]
#            vals = vals.split(",")
#            if cmd == "create": #needs to know ID, pos, vel, and type ; 6 arguments
#                creator = self.create_dict[vals[5]]
#                thisAgent = creator.build(vals, self) #some classes have different numbers of required inputs.  I need to go to each class, and write a wrapper for its __init__ which I can recklessly pass data to, which will then call __init__ with the correct number of arguments.  
#            elif cmd == "delete": #needs one parameter: ID
#                self.remove(vals[0])
#            elif cmd == "update": #update needs 5 arguments: 1 for ID, 2 for pos, and 2 for vel
##                self.agents[vals[0]].set_vel(float(vals[1]), float(vals[2]))
##                self.agents[vals[0]].set_pos(float(vals[3]), float(vals[4]))
#                self.agents[vals[0]].set_properties(vals)
#            elif cmd == "setship":
#                self.ID = vals[0]
#            elif cmd == "quit":
#                pass
#                #???? quit
        
        
    def handle_output(self, data):
        """
        |color:x0,y0:x1,y1:x2,y2:x3,y3
        """
        self.draw_string = data
#        to_draw = data.split("|")
#        del to_draw[0]
#        for shape in to_draw:
#            vals = shape.split(":")
#            color = vals[0]
#            points = []
#            for i in range(1, len(vals)):
#                pair = vals[i].split(",")
#                x, y= float(pair[0]), float(pair[1])
#                points = points + [Point2D(x, y)]
#            self.draw_shape(points, color)
#        print("did handle_output")
        self.pass_input()
#        self.update() #Trying a while loop inside of set_host() instead of a recursive thing:
        
        
    def pass_input(self):
        if self.GAME_OVER:
            rstr = "drop"
        else:
            rstr = ""
            for k in self.report_strings:
                rstr = rstr + "|" + k + ":" + str(self.report_strings[k]) 
        rstr = rstr.encode('ascii')
        len_data = str(len(rstr))
        to_send = ("0"*(16-len(len_data)) + len_data).encode('ascii') + rstr
        self.sock.sendall(to_send)
        if self.GAME_OVER:
            self.sock.close()