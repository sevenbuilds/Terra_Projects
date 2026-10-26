import pygame as py
import numpy as np
import math
from sys import exit

W, H = 800, 600
MASS = 1.0                       # 1kg
DAMPING = 0.5                    # DAMPING force (critical is ~7.75, lower = more bounce)
G = 9.8                          # 9.8 m/s^2 (100pxl = 1m)
STIFFNESS = 15.0                 # N/m
L0 = 300                         # rest length of spring in pxls
SUBSTEPS = 20                    # calculate physcis 20 times in 1 frame.
HEIGHT = 300
ANCHOR_X = 113
ANCHOR = np.array([ANCHOR_X, HEIGHT])
GROUND = 400

MASS_SIZE = 100
GROUND_TOP = HEIGHT + MASS_SIZE // 2        # top surface of the ground (mass sits on it)
WALL_LEFT = 100
EQ_POS = ANCHOR_X + L0                      # mass x when the spring is at rest
MIN_POS = ANCHOR_X + 60                     # shortest the spring can get
MAX_POS = W - MASS_SIZE - 10

# colors
BG_TOP = (30, 30, 34)
BG_BOTTOM = (18, 18, 20)
GROUND_C = (58, 58, 56)
GROUND_EDGE = (136, 135, 128)
WALL_C = (95, 94, 90)
HATCH_C = (120, 119, 112)
TEXT_C = (180, 178, 169)
TEXT_DIM = (136, 135, 128)
MASS_C = (29, 158, 117)
MASS_LIGHT = (93, 202, 165)
MASS_DARK = (8, 80, 65)
SPRING_REST = (239, 159, 39)                # amber at rest
SPRING_COMP = (55, 138, 221)                # blue when compressed
SPRING_STRETCH = (226, 75, 74)              # red when stretched
SPRING_OUTLINE = (20, 20, 22)
FORCE_SPRING = (175, 169, 236)              # lavender
FORCE_DAMP = (237, 147, 177)                # pink


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def spring_color(pos):
    d = max(-1.0, min(1.0, (pos - EQ_POS) / 150.0))
    if d < 0:
        return lerp_color(SPRING_REST, SPRING_COMP, -d)
    return lerp_color(SPRING_REST, SPRING_STRETCH, d)


def reset():
    pos = 450.0
    vel = 0.0
    return pos, vel

def calculate_forces(pos, vel):
    x = (pos - ANCHOR_X) - L0
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


def make_background(font_small):
    """Everything that never moves is drawn once here."""
    bg = py.Surface((W, H))
    for y in range(H):
        bg.fill(lerp_color(BG_TOP, BG_BOTTOM, y / H), (0, y, W, 1))

    # ground
    py.draw.rect(bg, GROUND_C, (WALL_LEFT, GROUND_TOP, W - WALL_LEFT, H - GROUND_TOP))
    py.draw.line(bg, GROUND_EDGE, (WALL_LEFT, GROUND_TOP), (W, GROUND_TOP), 3)
    for x in range(WALL_LEFT + 20, W, 24):
        py.draw.line(bg, HATCH_C, (x, GROUND_TOP + 12), (x - 10, GROUND_TOP + 26), 1)

    # wall with hatching on its outer side
    py.draw.rect(bg, WALL_C, (WALL_LEFT, 200, 26, GROUND_TOP - 200),
                 border_top_left_radius=4, border_top_right_radius=4)
    py.draw.line(bg, GROUND_EDGE, (WALL_LEFT, 200), (WALL_LEFT, GROUND_TOP), 2)
    for y in range(200, GROUND_TOP - 14, 14):
        py.draw.line(bg, HATCH_C, (WALL_LEFT, y + 14), (WALL_LEFT - 14, y), 2)

    # equilibrium marker
    for y in range(190, GROUND_TOP, 12):
        py.draw.line(bg, TEXT_DIM, (EQ_POS, y), (EQ_POS, y + 6), 1)
    label = font_small.render("equilibrium", True, TEXT_DIM)
    bg.blit(label, (EQ_POS - label.get_width() // 2, GROUND_TOP + 36))
    return bg


def draw_arrow(screen, color, start, dx, width=4):
    if abs(dx) < 3:
        return
    end = (start[0] + dx, start[1])
    py.draw.line(screen, color, start, end, width)
    s = 1 if dx > 0 else -1
    py.draw.polygon(screen, color, [end, (end[0] - 10 * s, end[1] - 7), (end[0] - 10 * s, end[1] + 7)])


def main():
    py.init()
    screen = py.display.set_mode((W,H))
    py.display.set_caption("Horizontal spring simulation.")
    clock = py.time.Clock()
    font = py.font.SysFont(("Consolas"),16)
    font_small = py.font.SysFont("Consolas", 14)
    font_big = py.font.SysFont("Consolas", 34, bold=True)

    background = make_background(font_small)
    hint = font_small.render("drag the mass    R reset    F forces    Esc quit", True, TEXT_DIM)
    panel = py.Surface((250, 150), py.SRCALPHA)
    py.draw.rect(panel, (0, 0, 0, 110), panel.get_rect(), border_radius=10)
    m_label = font_big.render("m", True, (225, 245, 238))

    running = True
    show_forces = True
    dragging = False
    grab_offset = 0.0
    pos, vel = reset()
    while running:
        frame_dt = min(1/30, clock.tick(60) / 1000.0)
        mass_rect = py.Rect(int(pos), HEIGHT - MASS_SIZE // 2, MASS_SIZE, MASS_SIZE)
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
            elif e.type == py.MOUSEBUTTONDOWN and e.button == 1:
                if mass_rect.collidepoint(e.pos):
                    dragging = True
                    grab_offset = e.pos[0] - pos
            elif e.type == py.MOUSEBUTTONUP:
                dragging  = False

        if dragging:
            vel = 0.0
            x, _ = py.mouse.get_pos()
            pos = min(max(x - grab_offset, MIN_POS), MAX_POS)
        elif not dragging:
            dt = frame_dt / SUBSTEPS
            for _ in range(SUBSTEPS):
                pos, vel = step(pos, vel, dt)
                if pos < MIN_POS:
                    pos = MIN_POS
                    vel = max(vel, 0)

        #---- rendering part -----

        screen.blit(background, (0, 0))
        mass_rect = py.Rect(int(pos), HEIGHT - MASS_SIZE // 2, MASS_SIZE, MASS_SIZE)
        hovered = mass_rect.collidepoint(py.mouse.get_pos())

        #---- mass shadow ----
        shadow = py.Surface((MASS_SIZE + 20, 16), py.SRCALPHA)
        py.draw.ellipse(shadow, (0, 0, 0, 90), shadow.get_rect())
        screen.blit(shadow, (mass_rect.x - 10, GROUND_TOP - 8))

        #---- spring ----
        pts = spring_points(ANCHOR, pos)
        color = spring_color(pos)
        py.draw.lines(screen, SPRING_OUTLINE, False, pts, 8)
        py.draw.lines(screen, color, False, pts, 5)
        py.draw.aalines(screen, lerp_color(color, (255, 255, 255), 0.45), False, pts)

        #---- draw pivot point ----
        py.draw.circle(screen, (44,44,42), ANCHOR, 2)
        py.draw.circle(screen, (44,44,42), ANCHOR, 10, 3)

        #---- mass ----
        body = lerp_color(MASS_C, MASS_LIGHT, 0.35) if (dragging or hovered) else MASS_C
        py.draw.rect(screen, body, mass_rect, border_radius=10)
        py.draw.rect(screen, MASS_LIGHT, (mass_rect.x + 8, mass_rect.y + 7, MASS_SIZE - 16, 5), border_radius=3)
        py.draw.rect(screen, MASS_DARK, mass_rect, 3, border_radius=10)
        screen.blit(m_label, m_label.get_rect(center=mass_rect.center))

        #---- forces and readout ----
        stretch = (pos - ANCHOR_X) - L0
        f_spring = -STIFFNESS * stretch
        f_damp = -DAMPING * vel
        if show_forces:
            cx = mass_rect.centerx
            top = mass_rect.y
            draw_arrow(screen, FORCE_SPRING, (cx, top - 20), max(-160, min(160, f_spring * 0.05)))
            draw_arrow(screen, FORCE_DAMP, (cx, top - 38), max(-160, min(160, f_damp * 0.05)))

            pe = 0.5 * STIFFNESS * stretch ** 2
            ke = 0.5 * MASS * vel ** 2
            screen.blit(panel, (16, 16))
            rows = [
                (f"x     {stretch:+9.1f} px", TEXT_C),
                (f"v     {vel:+9.1f} px/s", TEXT_C),
                (f"F_s   {f_spring:+9.1f}", FORCE_SPRING),
                (f"F_d   {f_damp:+9.1f}", FORCE_DAMP),
                (f"PE    {pe:9,.0f}", TEXT_C),
                (f"KE    {ke:9,.0f}", TEXT_C),
            ]
            for i, (text, col) in enumerate(rows):
                screen.blit(font.render(text, True, col), (28, 26 + i * 21))

        screen.blit(hint, (16, H - 28))

        py.display.update()
    py.quit()


if __name__ == "__main__":
    main()