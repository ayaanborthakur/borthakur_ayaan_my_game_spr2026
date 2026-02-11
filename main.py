

import math
import random
import sys
import pygame as pg
from settings import *
from sprites import *
from os import path
from utils import *
from math import floor

# overview - CONCISE AND INFORMATIVE
class Game:
   #initializes game instance
   def __init__(self):
      pg.init()
      self.clock = pg.time.Clock()
      self.screen = pg.display.set_mode((WIDTH, HEIGHT))
      pg.display.set_caption("Chris Cozort's awesome game!!!!!")
      self.playing = True
      #instanciates a 15 millisecond cooldown that can be used
      self.cooldown = Cooldown(15)
   
  
   def load_data(self):
        self.game_dir = path.dirname(__file__)
        self.map = Map(path.join(self.game_dir, 'level1.txt'))


   def new(self):
        #creating all the sprites and mobs and walls
        self.load_data()
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        
        self.all_mobs = pg.sprite.Group()
        self.all_mobs.add(Mob(self,10,10))
        for row,tiles in enumerate(self.map.data):
            for col,tile in enumerate(tiles):
                if tile == "1":
                    Wall(self,row,col)
                    print(row,col)
                if tile == "p":
                    self.player = Player(self,col,row)

        
     
   def run(self):
      #runs the game
      while self.playing == True:
            self.dt = self.clock.tick(FPS) / 1000
         
            self.events()
            self.update()
            self.draw()
        #if game loop ends quit pygame
      pg.quit()
    #manages keyboard and mouse events
   def events(self):
        for event in pg.event.get():
            if self.cooldown.ready() == True:
                self.cooldown.start()
                if event.type == pg.QUIT:
                    if self.playing:
                        self.playing= False

                    self.running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    pass
                if event.type == pg.MOUSEMOTION:
                    pass
                    
               
                    
                    
            
   def update(self):
        self.all_sprites.update()


   def draw_text(self, surface, text, size, color, x, y):
        font_name = pg.font.match_font('arial')
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x,y)
        surface.blit(text_surface, text_rect)
   def draw(self):
      self.screen.fill(WHITE)
      self.draw_text(self.screen, str(pg.time.get_ticks()-self.cooldown.start_time), 24, BLACK, 500, 100)
      self.all_sprites.draw(self.screen)
      pg.display.flip()


if __name__ == "__main__":
#    creating an instance or instantiating the Game class
   g = Game()
   g.new()
   g.run()
