import pygame as py 
import numpy as np 
import math 
from sys import exit 

def main():
    pygame.init()
    for e in pygame.event.get():
        if e.type == event.QUIT:
            exit()
            pygame.quit()
        elif e.type == pygame.event.KEYDOWN:
            if e.key == pygame.event.K_ESCAPE:
                exit()
                pygame.quit()

    pygame.display.update()

if __name__ == "__main__":
    main()