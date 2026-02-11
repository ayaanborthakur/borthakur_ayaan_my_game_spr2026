import pygame as pg
from pygame.sprite import Sprite
from settings import *
import math

vec = pg.math.Vector2

class Player(Sprite):
    def __init__(self, game, x, y):
        #intializes neccesary values
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface(TILESIZE)
        self.image.fill(BLACK)
        self.rect= self.image.get_rect()
        #physics vectors for acceleration postion and velocity
        self.accel = vec(0,0)
        self.vel = vec(0,0)
        self.pos = vec(x*32,y*32)
        #self.pos = vec(x,y) * TILESIZE[1]

    def update(self):
        #get keys and check if character is even moving
        is_moving = self.get_keys()
        #applying accelerationt o velocity and velocity to acceleration
        try:
            self.accel = self.accel.normalize() *ACCELERATION
            
            self.vel += self.accel
            if self.vel.magnitude() >= PLAYER_SPEED:
                
                self.vel = self.vel.normalize()*PLAYER_SPEED
           
            self.accel *= 0
            
        except:
            pass
        
       
        self.pos += self.vel
        self.rect.center = self.pos  
        #applysing friciton if player is not actively trying to move
        if not is_moving:
            self.vel*=0.89
        #checking if its hitting anything else
        for sprite in self.groups:
            if sprite != self:
                if self.rect.colliderect(sprite.rect):
                    print("hit")
        
    def get_keys(self):
        #gets keys and stuff
        keys = pg.key.get_pressed()

        value = False
        if keys[pg.K_w]:
            self.accel.y -= ACCELERATION
            value = True
        if keys[pg.K_a]:
            self.accel.x -= ACCELERATION
            value = True
        if keys[pg.K_s]:
            self.accel.y += ACCELERATION
            value = True
        if keys[pg.K_d]:
            self.accel.x += ACCELERATION
            value = True
        return value
        
    
        
        
        
class Mob(Sprite):
    #initialize the instance
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self,self.groups)
        self.game = game
        self.image = pg.Surface(TILESIZE)
        self.image.fill(GREEN)
        self.rect= self.image.get_rect()
        self.accel = vec(0,0)
        self.vel = vec(0,0)
        self.pos = vec(x*32,y*32)
        #self.pos = vec(x,y) * TILESIZE[1]

    def update(self):
        #calls movement toward player
        self.move(self.game.player.pos)
        #same as player
        try:
            
            if self.accel.magnitude() >= MOB_ACCELERATION:
                
                self.accel = self.accel.normalize() *MOB_ACCELERATION
            
            self.vel += self.accel
            if self.vel.magnitude() >= MOB_SPEED:
                
                self.vel = self.vel.normalize()*MOB_SPEED

            self.accel *= 0
            self.vel*=0.95
        except:
            pass
        
       
        self.pos += self.vel
        self.rect.center = self.pos  
       
    #gets teh neccesrary accleration to get to the player
    def move(self,pos):

        
        prevel = self.vel
        self.accel = pos-self.pos



class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self,self.groups)
        self.game = game
        self.image = pg.Surface(TILESIZE)
        self.image.fill(BLUE)
        self.rect= self.image.get_rect()
       
        self.vel = vec(0,0)
        self.pos = vec(x*32,y*32)
        #self.pos = vec(x,y) * TILESIZE[1]

    def update(self):
        self.rect.center = self.pos  
     
        
     
        
        
        
        
        