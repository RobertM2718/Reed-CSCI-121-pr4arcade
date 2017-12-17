from tkinter import *
from Game import Game, Agent
from geometry import Point2D, Vector2D
import math
import random


TIME_STEP = 0.5

def collide(a, b): #This isn't exactly object-oriented, but I still want it here.  
    if (a.position - b.position).magnitude() < a.radius + b.radius:
        a_dam = b.COLLISION_DAMAGE
        b_dam = a.COLLISION_DAMAGE
        a.damage(a_dam)
        b.damage(b_dam)

class MovingBody(Agent):

    def __init__(self, p0, v0, world):
        self.velocity = v0
        self.accel    = Vector2D(0.0,0.0)
        Agent.__init__(self,p0,world)
        

    def color(self):
        return "#000080"

    def shape(self):
        p1 = self.position + Vector2D( 0.125, 0.125)       
        p2 = self.position + Vector2D(-0.125, 0.125)        
        p3 = self.position + Vector2D(-0.125,-0.125)        
        p4 = self.position + Vector2D( 0.125,-0.125)
        return [p1,p2,p3,p4]

    def steer(self):
        return Vector2D(0.0)

    def update(self):
        self.position = self.position + self.velocity * TIME_STEP
        self.velocity = self.velocity + self.accel * TIME_STEP
        self.accel    = self.steer()
        self.world.trim(self)
    
    def set_pos(self, x, y):
        self.position = Point2D(x, y)
        
    def set_vel(self, x, y):
        self.velocity = Vector2D(x, y)
    
    def report(self):
        return self.ID + "," + str(self.position.x) + "," + str(self.position.y) + "," + str(self.velocity.dx) + "," + str(self.velocity.dy)
        
    def set_properties(self, vals): #the function Client uses to move its objects around.  
        self.set_pos(float(vals[1]), float(vals[2]))
        self.set_vel(float(vals[3]), float(vals[4]))
        
    def get_type(self):
        return "MovingBody"
    
    #builds are going to be a kind of function which (sort of) stands in for a __init__ function, to allow me to be agnostic about how many vals I'm passing to the constructor.  
    def build(vals, world): # vals[0] will be an ID
        p0 = Point2D(float(vals[1]), float(vals[2]))
        v0 = Vector2D(float(vals[3]), float(vals[4]))
        return MovingBody(p0, v0, world)

class Shootable(MovingBody):

    SHRAPNEL_CLASS  = None
    SHRAPNEL_PIECES = 0
    WORTH           = 1
    COLLISION_DAMAGE = 3
    STARTING_HEALTH = 1

    def __init__(self, position0, velocity0, radius, world):
        self.radius = radius
        MovingBody.__init__(self, position0, velocity0, world)
        self.health = self.STARTING_HEALTH

#    def is_hit_by(self, photon):
#        return ((self.position - photon.position).magnitude() < self.radius)

    def damage(self, n):
        self.health -= n
        if self.health < 1:
            self.explode()

    def explode(self):
        self.world.score += self.WORTH
        if self.SHRAPNEL_CLASS == None:
            return
        for _ in range(self.SHRAPNEL_PIECES):
            self.SHRAPNEL_CLASS(self.position,self.world)
        self.leave()
        
    def get_type(self):
        return "Shootable"

class Asteroid(Shootable):
    WORTH     = 5
    MIN_SPEED = 0.1
    MAX_SPEED = 0.3
    SIZE      = 3.0
    STARTING_HEALTH = 3 #?

    def __init__(self, position0, velocity0, world):
        Shootable.__init__(self,position0, velocity0, self.SIZE, world)
        self.world = world
        self.make_shape()

    def choose_velocity(self):
        return Vector2D.random() * random.uniform(self.MIN_SPEED,self.MAX_SPEED) * (60.0/self.world.FPS)
        
    def make_shape(self):
        angle = 0.0
        dA = 2.0 * math.pi / 15.0
        center = Point2D(0.0,0.0)
        self.polygon = []
        for i in range(15):
            if i % 3 == 0 and random.random() < 0.2:
                r = self.radius/2.0 + random.random() * 0.25
            else:
                r = self.radius - random.random() * 0.25
            dx = math.cos(angle)
            dy = math.sin(angle)
            angle += dA
            offset = Vector2D(dx,dy) * r
            self.polygon.append(offset)

    def shape(self):
        return [self.position + offset for offset in self.polygon]
    
    def get_type(self):
        return "Asteroid"

class ParentAsteroid(Asteroid):
    def __init__(self,world):
        self.world = world
        world.number_of_asteroids += 1
        velocity0 = self.choose_velocity()
        position0 = world.bounds.point_at(random.random(),random.random())
        if abs(velocity0.dx) >= abs(velocity0.dy):
            if velocity0.dx > 0.0:
                # LEFT SIDE
                position0.x = world.bounds.xmin
            else:
                # RIGHT SIDE
                position0.x = world.bounds.xmax
        else:
            if velocity0.dy > 0.0:
                # BOTTOM SIDE
                position0.y = world.bounds.ymin
            else:
                # TOP SIDE
                position0.y = world.bounds.ymax
        Asteroid.__init__(self,position0,velocity0,world)

    def explode(self):
        Asteroid.explode(self)
        self.world.number_of_asteroids -= 1
        
    def get_type(self):
        return "ParentAsteroid"

class Ember(MovingBody):
#    INITIAL_SPEED = 2.0
    START_SPEED = 2.0
#    SLOWDOWN      = 0.2
    SlOW_DOWN_BY = 0.2
#    TOO_SLOW      = INITIAL_SPEED / 20.0
    

    def __init__(self, position0, world):
        self.INITIAL_SPEED = self.START_SPEED * (60.0/world.FPS)
        self.TOO_SLOW = self.INITIAL_SPEED / 20.0
        self.SLOW_DOWN_BY = 0.2
        self.SLOWDOWN = self.SLOW_DOWN_BY * (60.0/world.FPS) #weird issues
        velocity0 = Vector2D.random() * self.INITIAL_SPEED
        MovingBody.__init__(self, position0, velocity0, world)

    def color(self):
        white_hot  = "#FFFFFF"
        burning    = "#FF8080"
        smoldering = "#808040"
        speed = self.velocity.magnitude()
        if speed / self.INITIAL_SPEED > 0.5:
            return white_hot
        if speed / self.INITIAL_SPEED > 0.25:
            return burning
        return smoldering

    def steer(self):
        return -self.velocity.direction() * self.SLOWDOWN

    def update(self):
        MovingBody.update(self)
        if self.velocity.magnitude() < self.TOO_SLOW:
            self.leave()
            
    def get_type(self):
        return "Ember"

class ShrapnelAsteroid(Asteroid):
    def __init__(self, position0, world):
        self.world = world
        world.number_of_shrapnel += 1
        velocity0 = self.choose_velocity()
        Asteroid.__init__(self, position0, velocity0, world)

    def explode(self):
        Asteroid.explode(self)
        self.world.number_of_shrapnel -= 1
        
    def get_type(self):
        return "ShrapnelAsteroid"

class SmallAsteroid(ShrapnelAsteroid):
    WORTH           = 20
    MIN_SPEED       = Asteroid.MIN_SPEED * 2.0
    MAX_SPEED       = Asteroid.MAX_SPEED * 2.0
    SIZE            = Asteroid.SIZE / 2.0
    SHRAPNEL_CLASS  = Ember
    SHRAPNEL_PIECES = 8

    def color(self):
        return "#A8B0C0"
    
    def get_type(self):
        return "SmallAsteroid"

class MediumAsteroid(ShrapnelAsteroid):
    WORTH           = 10
    MIN_SPEED       = Asteroid.MIN_SPEED * math.sqrt(2.0)
    MAX_SPEED       = Asteroid.MAX_SPEED * math.sqrt(2.0)
    SIZE            = Asteroid.SIZE / math.sqrt(2.0)
    SHRAPNEL_CLASS  = SmallAsteroid
    SHRAPNEL_PIECES = 3

    def color(self):
        return "#7890A0"
    
    def get_type(self):
        return "MediumAsteroid"

class LargeAsteroid(ParentAsteroid):
    SHRAPNEL_CLASS  = MediumAsteroid
    SHRAPNEL_PIECES = 2

    def color(self):
        return "#9890A0"
    
    def get_type(self):
        return "LargeAsteroid"

class Photon(MovingBody):
    INITIAL_SPEED = 2.0 * SmallAsteroid.MAX_SPEED
    LIFETIME      = 40
    COLLISION_DAMAGE = 1
    STARTING_HEALTH = 1
    RADIUS = 0.125

    def __init__(self,source,world):
        self.age  = 0
#        v0 = source.velocity + (source.get_heading() * self.INITIAL_SPEED)
        v0 = (source.get_firing_vector() * self.INITIAL_SPEED)*(60.0/world.FPS)
        self.health = self.STARTING_HEALTH
        self.radius = self.RADIUS
        self.source = source
        MovingBody.__init__(self, source.position, v0, world)
        self.left = False
        
    def damage(self, n):
        self.health -= n
        if self.health < 1 and not self.left: #again, 'x not in list' issue
            self.left = True
            Flash(self.position, self.world, 0.5, 4)
            self.leave()

    def color(self):
        return "#8080FF"

    def update(self):
        MovingBody.update(self)
        self.age += (60.0/self.world.FPS)
        if self.age >= self.LIFETIME and not self.left: #to try to avoid the 'x not in list' issue
            self.leave() 
        else:
            targets = [a for a in self.world.agents if isinstance(a,Shootable) or (isinstance(a, Missile) and (self.source != a.source))] #should this happen?  
            for t in targets:
                collide(self, t)
                
    def get_type(self):
        return "Photon"

class Missile(Photon):
    MAX_SPEED = 2.0
    LIFETIME = Photon.LIFETIME * 10
    ACCEL = 0.1 #twice Ship? A little bit more?  The same?  What's best?  
#    TURNS_IN_360   = 24
#    MAX__REL_SPEED = 0.001
    RADIUS = 0.25
    STARTING_HEALTH = 2 #was 3, but missiles were hard to shoot down.  
    def __init__(self, source, world, t_pos):
        Photon.__init__(self, source, world)
        self.ACCELERATION = self.ACCEL * (60.0/self.world.FPS)
        self.MAX_SPEED = Missile.MAX_SPEED*(60.0/self.world.FPS)
        self.heading = source.get_heading()
        self.velocity = source.velocity + source.get_heading()*self.INITIAL_SPEED*0.5 #don't need world.FPS here, because it incorporates a velocity already.  
        self.target = self.get_lock(t_pos)
        self.line = MissileTargetLine(self, self.target, self.world)
        
    def color(self):
        return "#FF0000"
    
    def shape(self): #copied from Ship.shape()
#        h  = self.heading
#        hp = h.perp()
#        p1 = self.position + h * 0.75
#        p2 = self.position + hp * 0.25
#        p3 = self.position - hp * 0.25
#        return [p1,p2,p3]
        d = 0.25
        p1 = self.position + Vector2D( d, d) #movingbody; just a bit bigger.  
        p2 = self.position + Vector2D(-d, d)        
        p3 = self.position + Vector2D(-d,-d)        
        p4 = self.position + Vector2D( d,-d)
        return [p1,p2,p3,p4]
        
    
    def update(self): #need to recalculate the 'lock' at each update
#        if self.velocity.magnitude() > 0:
#            self.heading = self.velocity.direction()
        Photon.update(self)
        self.heading = self.point()
        
    def trim_physics(self):
        m = self.velocity.magnitude()
        if m > self.MAX_SPEED:
            self.velocity = self.velocity * (self.MAX_SPEED / m)
        
    def leave(self): #overload to make an explosion on death?
        Flare(self.position, self.world, 3, 4) #lifetime was 2
        self.line.leave()
        if not isinstance(self.target, Ship):
            self.target.leave()
        Photon.leave(self)
        
    def steer(self): #change later so it pursues a target - falling in behind it, then ramming.  
        #should I make some sort of 'sticky' lock system, where it picks a target and then follows it unless it sees a much, much better one?  Would require storing the target on the missile.  
        
        #This one works
#        thrust = self.heading * self.ACCELERATION
#        match = (self.target.velocity - self.velocity).direction()*self.ACCELERATION*0.5
#        r_vec = thrust + match
        
        #This one might be better
        to_target = self.point()
#        to_target = (self.target.position-self.position)
        rel_vel = (self.velocity - self.target.velocity).direction()
#        rel_vel = (self.velocity-self.target.velocity)
        r_vec = (to_target - rel_vel).direction()*self.ACCELERATION
        
#        pos_locks = [s for s in self.world.agents if (isinstance(s, Ship) and (s != self.source))]
#        lock = None
#        lock_val = 0
#        for pos in pos_locks:
#            if lock != None: #this logic could probably be done better
#                vec = pos.position-self.position
#                val = vec.dot(self.heading) - vec.magnitude()/10
#                if val > lock_val:
#                    lock = pos
#                    lock_val = val
#                    r_vec = vec.direction() * self.ACCELERATION
#                
#            else:
#                lock = pos
#                vec = pos.position - self.position
#                lock_val = vec.dot(self.heading) - vec.magnitude()/10 #10 is a magic number
#                r_vec = vec.direction() * self.ACCELERATION
            
        return r_vec
    
    def point(self): #simplifying to work with a constant target
#        r_vec = self.heading*1.0 #remember; must be a float!
#        pos_locks = [s for s in self.world.agents if (isinstance(s, Ship) and (s != self.source))]
#        lock = None
#        lock_val = 0
#        for pos in pos_locks:
#            if lock != None: #this logic could probably be done better
#                vec = pos.position-self.position
#                val = vec.direction().dot(self.heading) - vec.magnitude()/10
#                if val > lock_val:
#                    lock = pos
#                    lock_val = val
##                    r_vec = vec.direction() * self.ACCELERATION
#                
#            else:
#                lock = pos
#                vec = pos.position - self.position
#                lock_val = vec.direction().dot(self.heading) - vec.magnitude()/10 #10 is a magic number
##                r_vec = vec.direction() * self.ACCELERATION
#        if lock != None:
#            vec_to_lock = (lock.position-self.position).direction()
#            rotate_by = self.heading.cross(vec_to_lock)
#            r_vec = (self.heading + self.heading.perp()*rotate_by*1.4).direction() #*1.4 is a magic number
#        vec_to_lock = (self.target.position-self.position).direction()
#        rotate_by = self.heading.cross(vec_to_lock) * 0.5 #experimental number
##        rotate_by = self.velocity.direction().cross(vec_to_lock) * 0.1 #will this help?  Not at all.  
#        r_vec = (self.heading + self.heading.perp()*rotate_by).direction()
#        return r_vec #make this smarter?  Maybe make the 'desired' heading be based on velocity?  
        return (self.target.position-self.position).direction()
    
    def get_lock(self, t_pos):
        lock = None
        pos_locks = [s for s in self.world.agents if (isinstance(s, Ship) and (s != self.source))]
        for pos in pos_locks:
            if lock != None:
                if ((pos.position - t_pos).magnitude() < (lock.position - t_pos).magnitude()):
                    lock = pos
            else:
                if (pos.position - t_pos).magnitude() < 5:
                    lock = pos
        if lock == None:
            lock = MovingBody(t_pos + Vector2D(), Vector2D(), self.world) #Build a special class for a missile locked onto space?  Or should it lock onto the cursor?  Or what?  
        return lock                 
    
    def get_firing_vector(self): #Later, change this so it launches photons in a ring?  For an explosion?  Maybe drops their velocity?  
        return self.heading
    
#    def trim_physics(self): #from Ship
#        MovingBody.trim_physics(self)

#        match = (self.target.velocity - self.velocity)
#        rel_speed = match.magnitude()
        
#        m = self.velocity.magnitude()
#        if m > self.MAX_SPEED:
#            self.velocity = self.velocity * (self.MAX_SPEED / m)
#        if True:#rel_speed > self.MAX_REL_SPEED:
#            self.velocity = (self.velocity + match*1.0) #brake?
    
class Flare(MovingBody):
    COLLISION_DAMAGE = 3
    
    def __init__(self, p0, world, radius, lifetime):
        MovingBody.__init__(self, p0, Vector2D(), world)
        self.COLLISION_DAMAGE = Flare.COLLISION_DAMAGE * (60.0/self.world.FPS)
        self.radius = radius
        self.lifetime = lifetime
        self.has_existed = 0
    def update(self):
        #MovingBody.update(self) I probably don't need this.  
        targets = [a for a in self.world.agents if isinstance(a, Asteroid) or isinstance(a, Ship) or isinstance(a, Missile)]
        for t in targets:
            collide(self, t)
        self.has_existed += (60.0/self.world.FPS)
        if self.has_existed >= self.lifetime:
            self.leave()
            
    def damage(self, n):
        pass
        
    def shape(self):
        points = []
        to_make = 20
        made = 0
        while made < to_make:
            angle = (360*made/to_make) * math.pi / 180.0
            vec = Vector2D(math.cos(angle), math.sin(angle))
            points.append(self.position + vec*float(self.radius))
            made += 1
        return points
        
    def color(self):
        return "#FFFFFF"
    
class Flash(Flare): #Like Flare, but does no damage, and does not collide.  A graphics experiment.  
    COLLISION_DAMAGE = 0
    
    def update(self):
        self.has_existed += (60.0/self.world.FPS)
        if self.has_existed >= self.lifetime:
            self.leave()

class MissileTargetLine(MovingBody):
    
    def __init__(self, m, t, w):
        self.missile = m
        self.target = t
        MovingBody.__init__(self, Point2D(), Vector2D(), w)
        
    def update(self):
        pass
    
    def color(self):
        return "#000080" #dark blue; change later?
    
    def shape(self):
        vec = self.target.position - self.missile.position
        h = vec.perp().direction()*0.03125
        p1 = self.missile.position + h
        p2 = self.missile.position - h
        p3 = self.missile.position + vec - h
        p4 = self.missile.position + vec + h
        return [p1, p2, p3, p4]

class Ship(MovingBody): #I have to find a way to update a ship's rotation
    TURNS_IN_360   = 24
    IMPULSE_FRAMES = 4
    ACCELERATION   = 0.05
    MAX_SPEED      = 2.0
    RADIUS = 1.0 #for collision
    FRAMES_TO_FIRE_MISSILE = 60 #one missile a second
    STARTING_HEALTH = 30
    COLLISION_DAMAGE = 3
    MAX_ENERGY = 450#600
    PHOTON_COST = 15#20
    STARTING_MISSILES = 3

    def __init__(self,world):
        self.TURNS_IN_360 = Ship.TURNS_IN_360*(60.0/world.FPS)
        self.ACCELERATION = Ship.ACCELERATION*(60.0/world.FPS)
        self.MAX_SPEED = Ship.MAX_SPEED*(60.0/world.FPS)
        self.FRAMES_TO_FIRE_MISSILE = Ship.FRAMES_TO_FIRE_MISSILE*world.FPS/60.0
        
        
        position0    = Point2D()
        velocity0    = Vector2D(0.0,0.0)
        self.dependants = [] #to keep track of what to get rid of when the player drops
        MovingBody.__init__(self,position0,velocity0,world)
        self.speed   = 0.0
        self.angle   = 90.0
        self.radius = Ship.RADIUS
        self.health = self.STARTING_HEALTH
        self.energy = self.MAX_ENERGY
        self.missiles = self.STARTING_MISSILES
        self.weapons_on = False
        self.firing_at = Point2D()
        self.braking = False        
        self.thrust = 0
        self.spin = 0
        self.firing_photons = False
        self.firing_missiles = False
        self.frames_till_missile = 0
        
        exhaust = ShipExhaust(self)
        self.dependants.append(exhaust)
        energy_indicator = EnergyIndicator(self)
        self.dependants.append(energy_indicator)
        missile_indicator = MissileIndicator(self)
        self.dependants.append(missile_indicator)
        
        #for when wrecked:
        self.wrecked = False
        self.spark_frames = 20
        self.since_spark = 30 #so the first spark isn't coming out during the initial burst

    def color(self):
        if self.wrecked:
            return "#626A77" #greyish
        else:
            return "#F0C080" 

    def get_heading(self):
        angle = self.angle * math.pi / 180.0
        return Vector2D(math.cos(angle), math.sin(angle))
    
    def get_firing_vector(self):
        return (self.firing_at - self.position).direction()
        
    def turn(self):
        self.angle += 360.0 / self.TURNS_IN_360 * self.spin * 60/self.world.FPS

    def shoot(self):
        if self.energy >= self.PHOTON_COST and self.weapons_on:
            Photon(self, self.world)
            self.energy -= self.PHOTON_COST
#        print("shots fired")
    
    def launch_missile(self):
        if self.missiles > 0 and self.weapons_on:
            Missile(self, self.world, self.firing_at)
            self.frames_till_missile = self.FRAMES_TO_FIRE_MISSILE
            self.missiles -= 1
    
    def shape(self):
        h  = self.get_heading() #trying to double the size, roughly.  Might have to push it a little backwards, too.  
        
        hp = h.perp() #instead of self.position, how about self.back()
        b = self.back()
        p1 = b + h * 2.0
        p2 = b + hp * 0.5 * 1.5
        p3 = b - hp * 0.5 * 1.5
        return [p1,p2,p3]

    def steer(self):
        if not self.wrecked:
            t_part = self.get_heading() * self.ACCELERATION * self.thrust
            b_part = self.velocity.direction() * -1.0 * self.ACCELERATION * self.braking
            return t_part + b_part
        else:
            return Vector2D()


    def trim_physics(self):
#        MovingBody.trim_physics(self) #I'm pretty sure that trim_physics() never gets called, and also that MovingBody doesn't HAVE a trim_physics()
        m = self.velocity.magnitude()
        if m > self.MAX_SPEED:
            self.velocity = self.velocity * (self.MAX_SPEED / m)
#            self.impulse = 0
            
    def set_property(self, pv): # pv is a property-value pair
        if pv[0] == "thrust":
            self.thrust = float(pv[1])
            
        elif pv[0] == "spin":
            self.spin = float(pv[1])
            
        elif pv[0] == "firing_photons":
            self.firing_photons = (pv[1] == "True")
#            print(pv[1], self.firing_photons)
#            if self.firing_photons:
#                print("tested as True")
            
        elif pv[0] == "firing_missiles":
            self.firing_missiles = (pv[1] == "True")
            
        elif pv[0] == "firing_at":
            if pv[1] == 'mouseoff':
                self.firing_at = self.position + self.get_heading()*2.0
            else:
                xy = [float(i) for i in pv[1].split(",")]
                self.firing_at = Point2D(xy[0], xy[1])
            
        elif pv[0] == "braking":
            self.braking = float(pv[1])
            
            
            
            
    def update(self):
#        print("updoot")
        MovingBody.update(self)
        if not self.wrecked:
            self.turn()
            if self.firing_photons:
    #            print("Check: photons")
                self.shoot()
            if self.firing_missiles and (self.frames_till_missile == 0):
                self.launch_missile()
            if self.frames_till_missile > 0:
                self.frames_till_missile -= 1
        else:
            if self.since_spark <= 0:
                Ember(self.position, self.world)
                self.since_spark = self.spark_frames
            self.since_spark -= 1
            
        if self.energy < self.MAX_ENERGY:
            self.energy += (60.0/self.world.FPS) #should I make it so that energy is only ever an int?  
#        if self.thrust > 0: #To try to give the ships an exhaust trail
#            em = Ember(self.position, self.world)
#            new_vel = -0.5 * em.velocity.magnitude() * self.get_heading() #the -0.5 instead of -1 is to make the trail not quie so long
#            em.velocity = new_vel
            #The embers are cool, but I think for now I'll try to keep the number of objects in the world lower.  When I'm doing latency tests, I'll see if the embers matter.  
        targets = [a for a in self.world.agents if isinstance(a, Asteroid) or (isinstance(a, Photon) and a.source != self)]
        for t in targets:
            collide(self, t)
        self.trim_physics() #Should this happen?  Does this improve gameplay? 
            
    def damage(self, n):
        self.health -= n
        if self.health < 1:
            self.wreck()
            
    def wreck(self):
        if not self.wrecked:
            self.wrecked = True
            for _ in range(10):
                Ember(self.position, self.world)
            Flare(self.position, self.world, 5, 3)
        
#    def is_hit_by(self, asteroid): #a modification of the Shootable class' is_hit_by() method.  
#        return ((self.position - asteroid.position).magnitude()) < (asteroid.radius + self.radius)
    
#    def get_type(self):
#        return "Ship"
    
    def remove_dependants(self):
        for d in self.dependants:
            d.leave() #more elegant than self.world.remove(d), I think, though it amounts to the same thing.  
    
    def back(self):
        return self.position-self.get_heading()*0.5 #arbitrary constant; pushes the shape of the ship back from its center of collision
    
    def toggle_weapons(self):
        self.weapons_on = not self.weapons_on
        
    def player_marker(self): #builds the whole command string to draw the player-marking shape
        points = self.shape()
        
        r_points_1 = [p + ((p-self.position).direction() * 0.4) for p in points]
        r_points_2 = [p + ((p-self.position).direction() * 0.2) for p in points]
        color_1 = "#47C421" #bright green
        color_2 = "#000000" #black
        r_str = "|" + color_1
        for p in r_points_1:
            r_str += ":" + str(round(p.x, 4)) + "," + str(round(p.y, 4))
        r_str += "|" + color_2
        for p in r_points_2:
            r_str += ":" + str(round(p.x, 4)) + "," + str(round(p.y, 4))
        return r_str
    
    
class ShipExhaust(MovingBody): #Alternatively, I could have the ship fire embers backwards?  
    def __init__(self, ship): #This could cause problems when a player drops their connection and the ship is removed from the world.  edit: Turns out it does - I need to find a way to remove the exhaust.  Also, I need to deal with the weird input error I think I had.  
        self.ship = ship #I got an error for not passing p0 or v0 to ShipExhaust.  I guess I'll include them.  
        MovingBody.__init__(self, self.ship.position, Vector2D, self.ship.world)
    def update(self): #Turns out the error above was that I had init__ instead of __init__
#        self.position = self.ship.position + Vector2D() #to hopefully copy the object
        self.position = self.ship.back()
    def shape(self):
        if self.ship.thrust > 0 and not self.ship.wrecked:
            h = -0.7*self.ship.get_heading() # the -1 is necessary; the 0.7 is arbitrary
            hp = h.perp()
            p1 = self.position + h
            p2 = self.position + hp * 0.5
            p3 = self.position - hp * 0.5
            return [p1, p2, p3]
        else:
            return [self.position, self.position]
    def color(self):
        return "#EF6221" #A dull orange
    
class EnergyIndicator(Flash):
    RADIUS = 0.575 - 0.15 #determined by trigonometry
    
    def __init__(self, ship):
        self.ship = ship
        Flash.__init__(self, self.ship.position, self.ship.world, self.RADIUS, 10) #The 10 is only there because Flash.__init__ requires me to pass a value for the lifetime, even if I'm not going to use it.  
    
    def update(self):
        self.position = self.ship.position + Vector2D() #Again, to avoid copying
        
    def color(self): #This is the same method of converting to hex I used in Boids.  
        if self.ship.wrecked:
            return self.ship.color()
        else:
            percent = self.ship.energy/self.ship.MAX_ENERGY
            color_value = int(1-255 * percent)
            all_hex = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
            return "#" + (all_hex[color_value // 16] + all_hex[color_value % 16])*2 + "FF"
#        return "#0000" + all_hex[color_value // 16] + all_hex[color_value % 16] #Change later to be based on ship.energy
        
        
class MissileIndicator(EnergyIndicator):
    RADIUS = 0.2
    def update(self):
        self.position = self.ship.position + self.ship.get_heading() * 1.5
            
    def shape(self):
        if self.ship.frames_till_missile == 0 and self.ship.missiles >= 1 and not self.ship.wrecked:
            return EnergyIndicator.shape(self)
        else:
            return [self.position + Vector2D(), self.position + Vector2D()]
        
    def color(self):
        return "#FF0000" #red

#class PlayAsteroids(Game):
#
#    DELAY_START      = 150
#    MAX_ASTEROIDS    = 6
#    INTRODUCE_CHANCE = 0.01
#    
#    def __init__(self):
#        Game.__init__(self,"ASTEROIDS!!!",60.0,45.0,800,600,topology='wrapped')
#
#        self.number_of_asteroids = 0
#        self.number_of_shrapnel = 0
#        self.level = 1
#        self.score = 0
#
#        self.before_start_ticks = self.DELAY_START
#        self.started = False
#
#        self.ship = Ship(self)
#
#    def max_asteroids(self):
#        return min(2 + self.level,self.MAX_ASTEROIDS)
#
#    def handle_keypress(self,event):
#        Game.handle_keypress(self,event)
#        if event.char == 'i':
#            self.ship.speed_up()
#        elif event.char == 'j':
#            self.ship.turn_left()
#        elif event.char == 'l':
#            self.ship.turn_right()
#        elif event.char == ' ':
#            self.ship.shoot()
#        
#    def update(self):
#
#        # Are we waiting to toss asteroids out?
#        if self.before_start_ticks > 0:
#            self.before_start_ticks -= 1
#        else:
#            self.started = True
#        
#        # Should we toss a new asteroid out?
#        if self.started:
#            tense = (self.number_of_asteroids >= self.max_asteroids())
#            tense = tense or (self.number_of_shrapnel >= 2*self.level)
#            if not tense and random.random() < self.INTRODUCE_CHANCE:
#                LargeAsteroid(self)
#
#        Game.update(self)
            

        

#print("Hit j and l to turn, i to create thrust, and SPACE to shoot. Press q to quit.")
#game = PlayAsteroids()
#while not game.GAME_OVER:
#    time.sleep(1.0/60.0)
#    game.update()
