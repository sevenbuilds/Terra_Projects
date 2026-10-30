import pygame as py 
import numpy as np
import math 
from sys import exit 

W, H = 800, 600
MASS = 1.0                       # 1kg
DAMPING = 1.5                    # DAMPING force
G = 9.8                          # 9.8 m/s^2 (100pxl = 1m)
STIFFNESS = 15.0                 # N/m
L0 = 300                         # rest length of spring in pxls
SUBSTEPS = 20                    # calculate physcis 20 times in 1 frame.
HEIGHT = 300
ANCHOR = np.array([113, HEIGHT])
GROUND = 400
MIN_LEN = 60
MIN_POS = ANCHOR[0] + MIN_LEN

# colors
white = (255,255,255)
black = (0,0,0)

def reset():
    pos = 450.0
    vel = 0.0
    return pos, vel

def calculate_forces(pos, vel):
    x = (pos - ANCHOR[0]) - L0
    f_spring = -STIFFNESS * x
    f_damping = -DAMPING * vel
    net_force = f_spring + f_damping 
    return net_force

def step(pos, vel, dt):
    f = calculate_forces(pos, vel)
    acceleration = f / MASS
    vel = vel + (acceleration * dt)
    pos = pos + (vel * dt)
    return pos, vel

def spring_points(a, b, loop=7, coils=9, lead=0.10, width=20.0, samples= 240):
    vector = np.array([b, HEIGHT])
    d = vector - a
    length = np.linalg.norm(d)
    unit_vector = d / length
    normal = np.array([-unit_vector[1], unit_vector[0]])
    start =  a + (unit_vector * length * lead)
    body = length * (1 - 2 * lead)
    pts = [a, start]
    for i in range(samples + 1):
        t = i / samples
        phase =  2 * math.pi * coils * t
        along = body * t - loop *( 1- math.cos(phase))
        side = width * math.sin(phase)
        pts.append(start + unit_vector * along + normal * side)
    pts.append(vector)
    return pts

def main():
    py.init()
    screen = py.display.set_mode((W,H))
    title = py.display.set_caption("Horizontal spring simulation.")
    clock = py.time.Clock()
    font = py.font.SysFont(("Consolas"),16)

    running = True
    show_forces = True
    dragging = False
    pos, vel = reset()
    while running:
        frame_dt = min(1/30, clock.tick(60) / 1000.0)
        for e in py.event.get():
            if e.type == py.QUIT:
                running = False
                py.quit()
                exit()
            elif e.type == py.KEYDOWN:
                if e.key == py.K_ESCAPE:
                    running = False
                    py.quit()
                    exit()
                elif e.key == py.K_r:
                    reset()
                    dragging = False
                elif e.key == py.K_f:
                    show_forces = not show_forces
            elif e.type == py.MOUSEBUTTONDOWN:
                mouse = e.pos
                if np.linalg.norm(mouse - np.array([pos, HEIGHT])) < 110:
                    dragging = True
            elif e.type == py.MOUSEBUTTONUP:
                dragging  = False

        if dragging:
            vel = 0.0
            x, _ = py.mouse.get_pos()
            pos = max(x, MIN_POS)
        elif not dragging:
            dt = frame_dt / SUBSTEPS
            for _ in range(SUBSTEPS):
                pos, vel = step(pos, vel, dt)
                if pos < MIN_POS:
                    pos = MIN_POS
                    vel = abs(vel) * 0.3 
            
        #---- rendering part -----

        screen.fill((25,25,25))
        py.draw.line(screen, (95, 94, 90), (113, 400), (113, 200), 25)
        py.draw.line(screen, (180, 180, 180), (100, 400), (700, 400), 100)

        #---- draw pivot point ----
        py.draw.circle(screen, (44,44,42), ANCHOR, 2)
        py.draw.circle(screen, (44,44,42), ANCHOR, 10, 3)

        #---- spring ----
        pts = spring_points(ANCHOR, pos)
        py.draw.lines(screen, (180, 178, 169), False, pts, 3)

        #---- mass ----
        #pygame.draw.rect(surface, color, (x, y, width, height), border_radius=0)
        py.draw.rect(screen, (29,158,117), (pos, HEIGHT - 49, 100, 100))


        py.display.update()
    py.quit()


if __name__ == "__main__":
    main()