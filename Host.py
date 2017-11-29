# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 14:31:06 2017

@author: Robert
"""

#need a scheme to keep track of IDs.  Make a set of all allowed IDs?

import PlayAsteroids
import random
import sys
from geometry import Bounds, Point2D, Vector2D
from tkinter import *
import socket

import string
def all_IDs(): #this is how I'll make sure I don't give two objects the same name.  This technically allows only a finite number of objects, but it should be far more objects than I need.  
    rset = set()
    allowed_characters = [str(i) for i in range(10)] + [i for i in string.ascii_uppercase]
    for i in allowed_characters:
        for j in allowed_characters:
            for k in allowed_characters:
                rset.add(i + j + k)
    return rset

class Host(Frame): #inherit from Game?
    """
    Handles all server-side operations; also maintains connections with Clients and communicates at each game cycle
    """
    
    DELAY_START      = 150
    MAX_ASTEROIDS    = 6
    INTRODUCE_CHANCE = 0.01
    #server_address = ("localhost", 10000)
    def __init__(self, name, w, h, ww, wh, topology = 'wrapped', console_lines = 0, port = 10000, num_cns = 1): #need to add options so running Main lets you choose your port.  
        
        #stuff I need (from Frame) but don't want.  Remove?
        
        # Register the world coordinate and graphics parameters.
        self.WINDOW_WIDTH = ww
        self.WINDOW_HEIGHT = wh
        self.bounds = Bounds(-w/2,-h/2,w/2,h/2)
        self.topology = topology
        
#        self.num_frames = 0
        
        # actual host:
        self.connections = [] #for now, this will be a pointer to the Client object.  I will need to change this when I go multiplayer.  
        self.agents = [] #storing agents in a dictionary, rather than in a list, because it makes it easier to think about how to construct the command string.  
        self.ships = [] #how does this work with closing connections?
        self.available_IDs = all_IDs()
        
        self.number_of_asteroids = 0
        self.number_of_shrapnel = 0
        
        self.before_start_ticks = self.DELAY_START
        self.started = False
        
        self.command_string = ""
        
        self.level = 3 #deal with this later
        self.score = 0
        
        self.GAME_OVER = False #should I include a way for the host to terminate the game, kicking out all the clients?  
        
        #network stuff:
        IP = socket.gethostbyname(socket.gethostname())
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (IP, port) #does this need to go later?  Can I just make this work with localhost, and still have others connect to it?          
        print('starting up on {} port {}'.format(*server_address))
        self.sock.bind(server_address)
        self.sock.listen(num_cns) #should I be printing the ip address near here?
        connections_formed = 0
        while connections_formed < num_cns: #Do I need to close each connection after each pass, and re-open it later?  
            print("broadcasting on", self.sock.getsockname()[0])
            print("Waiting for a connection.  Currently connected:", connections_formed, "out of", num_cns)
            connection, client_address = self.sock.accept()
            print ("Connection from", client_address, "\n")
            self.add_connection((connection, client_address))
            connections_formed += 1
        self.address = server_address
        
    def add_connection(self, cn):  
        self.connections.append(cn)
        ship = PlayAsteroids.Ship(self)
        self.ships.append(ship)
#        cn.receive_ID(ship.ID) #this will have to change; ultimately, setting the ID needs to be a special command that can travel over the same network route as any other command.  
#        self.pass_output() #to make sure that the clients have a copy of the ship
        
        
    def drop_connection(self, cn):
        print("Client at", cn[1], "dropped")
        ship_index = self.connections.index(cn)
        ship = self.ships[ship_index]
        self.ships.remove(ship) #to fix the problem with the ships staying around after the connection dropped.  
        self.agents.remove(ship)
        cn[0].close()
        self.connections.remove(cn)
        if len(self.connections) == 0:
            self.sock.close() #is this going to cause errors?
            self.GAME_OVER = True
            
        
    def trim(self, agent): #holding measure - this is an important part of the game engine, and needs to be addressed.  
        if self.topology == 'wrapped':
            agent.position = self.bounds.wrap(agent.position)
        elif self.topology == 'bound':
            agent.position = self.bounds.clip(agent.position)
        elif self.topology == 'open':
            pass
        
    def max_asteroids(self):
        return min(2 + self.level,self.MAX_ASTEROIDS)
    
    def receive_input(self):
        data_list = []
        for c in self.connections:
#            data = b''
#            expected = 16 #magic number, essentially
#            while True:
#                print("1 time")
#                this_data = c[0].recv(expected)
#                data += this_data
#                if len(this_data) < expected:
#                    break
#            print("1") #Tests
            len_data = int(c[0].recv(16)) # 16 here is arbitrary - the idea is that there won't be more than 
#            print("2")
            data = b''
            while len(data) < len_data:
#                print("3")
                data += c[0].recv(4096) # also arbitrary
            data_list.append(data.decode('ascii'))
        self.handle_input(data_list)
    
    def handle_input(self, data_list): #TODO #????
        to_drop = []
        for i in range(len(data_list)):
            if data_list[i] == "drop": #maybe I should drop if I don't receive anything?  Might that work better?  
                to_drop.append(self.connections[i])
            else:
                parts = data_list[i].split("|")
                del parts[0]
#                print("parts = ",parts)
                ship = self.agents[i]
                for p in parts:
                    ship.set_property(p.split(":"))
        for cn in to_drop:
            self.drop_connection(cn)
    
    def update(self):
        
        self.receive_input()
        
        self.command_string = "" #first 'command' will be null?  Shouldn't matter.  
        #                           Turns out it does, but I can resolve that in Client.  
        if self.before_start_ticks > 0:
            self.before_start_ticks -= 1
        else:
            self.started = True
            
        
        if self.started:
            tense = (self.number_of_asteroids >= self.max_asteroids())
            tense = tense or (self.number_of_shrapnel >= 2*self.level)
            if not tense and random.random() < self.INTRODUCE_CHANCE:
                PlayAsteroids.LargeAsteroid(self)
        
        for agent in self.agents:
            agent.update()
#            self.command_string += "|update:" + self.agents[ID].report()
            
        for agent in self.agents:
            self.command_string += "|" + agent.color()
            point_list = agent.shape()
            for p in point_list:
                self.command_string += ":" + str(round(p.x, 3)) + "," + str(round(p.y, 3)) #the 3 here is a magic number.  
                #Adding round() here - it shouldn't reduce display accuracy by much, but it ought to cut down the size of the command string by a lot.  
        self.pass_output()
#        print(self.command_string)
#        self.num_frames += 1
#        print ("Agents:", self.agents)
            
        
        
    def pass_output(self):
        cmds = self.command_string.encode('ascii')
        len_data = str(len(cmds))
        to_send = ("0"*(16-len(len_data)) + len_data).encode('ascii') + cmds
        for c in self.connections:
            c[0].sendall(to_send)
    
    def add(self, agent):
        self.agents.append(agent)
#        self.command_string += "|create:" + agent.report() + "," + agent.get_type()
        
    def remove(self, agent):
        self.agents.remove(agent)
#        self.command_string += "|delete:" + agent.report()
        