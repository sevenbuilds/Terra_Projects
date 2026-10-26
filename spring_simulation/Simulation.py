import pygame as py 
import numpy as np
import math 
from sys import exit 

W, H = 800, 600
MASS = 1.0                       # 1kg
DAMPING = 0.5                    # DAMPING force
G = 9.8                          # 9.8 m/s^2 (100pxl = 1m)
STIFFNESS = 15.0                 # N/m
L0 = 300                         # rest length of spring in pxls
SUBSTEPS = 20                    # calculate physcis 20 times in 1 frame.
HEIGHT = 300
ANCHOR = np.array([113, HEIGHT])
GROUND = 400
MIN_LEN = 60
MIN_POS = ANCHOR[0] + MIN_LEN
EQ_X = 413
MASS_SIZE = 100

# colors
white = (255,255,255)
black = (0,0,0)
SPRING_REST = (239, 159, 39)                # amber at rest
SPRING_COMP = (55, 138, 221)                # blue when compressed
SPRING_STRETCH = (226, 75, 74)              # red when stretched
GROUND_C = (58, 58, 56)
GROUND_EDGE = (136, 135, 128)
SPRING_OUTLINE = (20, 20, 22)
TEXT_C = (180, 178, 169)
FORCE_SPRING = (175, 169, 236)              # lavender
FORCE_DAMP = (237, 147, 177)                # pink

def reset():
    pos = 450.0
    vel = 0.0
    return pos, vel

def calculate_forces(pos, vel):
    x = (pos - ANCHOR[0]) - L0
    f_spring = -STIFFNESS * x
    f_damping = -DAMPING * vel
    net_force = f_spring + f_damping 
    return net_force, f_spring, f_damping

def step(pos, vel, dt):
    f, _, _ = calculate_forces(pos, vel)
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

def lerp_color(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))

def spring_color(pos):
    d = max(-1, min(1, (pos - EQ_X) / 150.0))
    if d < 0:
        return lerp_color(SPRING_REST, SPRING_COMP, -d)
    return lerp_color(SPRING_REST, SPRING_STRETCH, d)

def arrow(surface, color, start, dx, width=4):
    if abs(dx) < 3:
        return
    end = start[0] + dx, start[1]
    s = 1 if dx > 0 else -1
    py.draw.line(surface, color, start, end, width)
    py.draw.polygon(surface, color, [end, (end[0] - 10 * s, end[1] + 7), (end[0] - 10 * s, end[1] - 7)])
    
def main():
    py.init()
    screen = py.display.set_mode((W,H))
    title = py.display.set_caption("Horizontal spring simulation.")
    clock = py.time.Clock()
    font_small = py.font.SysFont(("Consolas"),16) 
    font_big = py.font.SysFont(("Consolas"),32)
    m_font = font_big.render("m",True,(225, 245, 238))
    equilibrium_text = font_small.render("Equilibrium", True, TEXT_C)

    running = True
    show_forces = True
    dragging = False
    pos, vel = reset()
    while running:
        frame_dt = min(1/30, clock.tick(60) / 1000.0)
        mass_rect = py.Rect(int(pos), HEIGHT - (MASS_SIZE // 2), MASS_SIZE, MASS_SIZE)
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
                    pos, vel = reset()
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
        py.draw.line(screen, GROUND_EDGE, (100, 400), (100, 200), 2)
        for y in range(190, GROUND, 12):
            py.draw.line(screen, (136, 135, 128), (EQ_X - 1, y), (EQ_X - 1, y + 6), 1)
        py.draw.line(screen, GROUND_C, (0, 500), (W - 5, 500), 295)
        py.draw.line(screen, GROUND_C, (0, 400), (W - 5, 400), 100)
        py.draw.line(screen, GROUND_EDGE, (0, 350), (W - 5, 350), 3)

        #---- draw slash lines ---- 
        for x in range(0, W-5, 20):
            py.draw.line(screen, GROUND_EDGE, (x, 360), (x - 10, 360 - 10), 2)
        for y in range(210, 350, 20):
            py.draw.line(screen, GROUND_EDGE, (100, y), (100 - 10, y - 10), 2)


        #---- draw pivot point ----
        py.draw.circle(screen, (44,44,42), ANCHOR, 2)
        py.draw.circle(screen, (44,44,42), ANCHOR, 10, 3)

        #---- spring ----
        color = spring_color(pos)
        pts = spring_points(ANCHOR, pos)
        py.draw.lines(screen, SPRING_OUTLINE, False, pts, 8)
        py.draw.lines(screen, color, False, pts, 5)
        py.draw.aalines(screen, lerp_color(color, (255,255,255), 0.45), False, pts)

        #---- shadow ----
        shadow = py.Surface((MASS_SIZE + 20, 16), py.SRCALPHA)
        py.draw.ellipse(shadow, (0,0,0,90), shadow.get_rect())
        screen.blit(shadow, (pos - 7, HEIGHT + 45))

        #---- mass ----
        #pygame.draw.rect(surface, color, (x, y, width, height), border_radius=0)
        py.draw.rect(screen, (29,158,117), (pos, HEIGHT - 49, 100, 100), border_radius=10)
        py.draw.rect(screen, (32,86,69), (pos, HEIGHT - 49, 100, 100), 5, border_radius=10)
        start_pos = pos + 15, HEIGHT - 35
        end_pos =  pos + 85, HEIGHT - 35
        fade_surface = py.Surface((W,H), py.SRCALPHA)
        py.draw.line(fade_surface, (255,255,255,75), start_pos, end_pos, 5)
        py.draw.circle(fade_surface, (255,255,255,75), start_pos, 2)
        py.draw.circle(fade_surface, (255,255,255,75), end_pos, 2)
        screen.blit(fade_surface, (0,0))
        screen.blit(m_font, (pos + 40, HEIGHT - 13))

        #---- show-forces ----
        _, f_spring, f_damping = calculate_forces(pos, vel)
        if show_forces:
            center_x = mass_rect.centerx
            top = mass_rect.y
            arrow(screen, FORCE_SPRING, (center_x, top - 20), max(-160,min(160, f_spring * 0.05)))
            arrow(screen, FORCE_DAMP, (center_x, top - 38), max(-160,min(160, f_damping * 0.05)))

        #---- texts ----
        screen.blit(equilibrium_text, (EQ_X - 40, 370))

        py.display.update()
    py.quit()


if __name__ == "__main__":
    main()