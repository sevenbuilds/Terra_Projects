import pygame as py 
import numpy as np
import math 
from sys import exit 

W, H = 800, 600        
G = 9.8                          # 9.8 m/s^2 (100pxl = 1m)       
L0 = 300                         # rest length of spring in pxls
SUBSTEPS = 20                    # calculate physcis 20 times in 1 frame.
HEIGHT = 300
GROUND = 400
MIN_LEN = 60
ANCHOR = np.array([113, HEIGHT])
MIN_POS = ANCHOR[0] + MIN_LEN
EQ_X = 413

mass_SIZE = 100
mass = 5.0                  
damping = 2.0
stiffness = 100.0                    

MAX_mass = 50.0
MAX_stiffness = 500.0
MAX_damping = 20.0

MIN_mass = 1.0
MIN_stiffness = 1.0
MIN_damping = 1.0

# colors
white = (255,255,255)
black = (0,0,0)

GROUND_C = (58, 58, 56)
GROUND_EDGE = (136, 135, 128)
SPRING_OUTLINE = (20, 20, 22)
TEXT_C = (180, 178, 169)
FORCE_SPRING = (175, 169, 236)              # lavender
FORCE_DAMP = (237, 147, 177)                # pink
SPRING_REST = (239, 159, 39)                # amber at rest
SPRING_COMP = (55, 138, 221)                # blue when compressed
SPRING_STRETCH = (226, 75, 74)              # red when stretched

def reset():
    pos = 450.0
    vel = 0.0
    return pos, vel

def calculate_forces(pos, vel):
    x = (pos - ANCHOR[0]) - L0
    f_spring = -stiffness * x
    f_damping = -damping * vel
    net_force = f_spring + f_damping 
    return net_force, f_spring, f_damping

def step(pos, vel, dt):
    f, _, _ = calculate_forces(pos, vel)
    acceleration = f / mass
    vel = vel + (acceleration * dt)
    pos = pos + (vel * dt)
    return pos, vel

def spring_points(a, b, loop=7, coils=9, lead=0.10, width=20.0, samples= 240):
    vector = np.array([b, HEIGHT])
    d = vector - a
    length = np.linalg.norm(d)
    mid_point = (a + vector) / 2
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
    return pts, mid_point

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
    py.draw.polygon(
        surface, 
        color, 
        [end, (end[0] - 10 * s, end[1] + 7), (end[0] - 10 * s, end[1] - 7)]
    )

def draw_displacement_graph(surface, rect, time_data, displacement_data):

    x, y, width, height = rect

    py.draw.rect(surface, (32,32,32), rect, border_radius=5)

    for i in range(1,5):
        gx = x + i * width // 5
        py.draw.line(
            surface,
            (65,65,65),
            (gx, y),
            (gx, y + height),
            1
        )

    for i in range(1, 5):
        gy = y + i * height // 5
        py.draw.line(
            surface,
            (65,65,65),
            (x , gy),
            (x + width, gy),
            1
        )

    if len(time_data) < 2:
            return    

    end_time = time_data[-1]
    start_time = max(0, end_time - 10)

    max_displacement = max(
        abs(value) for value in displacement_data
    )

    scale = max(20, max_displacement * 1.15)

    center_y = y + height // 2

    py.draw.line(
        surface, 
        (140, 140, 140),
        (x, center_y),
        (x + width, center_y),
        1
    )

    points = []

    for t, displacement in zip(time_data, displacement_data):

        if t < start_time:
            continue

        px = x + ((t - start_time) / 10) * width
        py_pos = center_y - (displacement / scale) * (height / 2)
        points.append((int(px), int(py_pos)))

    if len(points) > 1:
        py.draw.lines(
            surface, 
            (100,200,255),
            False,
            points,
            2
        )


def draw_energy_graph(surface, rect, time_data, KE_data, PE_data, peak_energy):
    x, y, width, height = rect

    py.draw.rect(surface, (32, 32, 32), rect, border_radius=5)

    for i in range(1, 5):
        gx = x + i * width // 5
        py.draw.line(surface, (65, 65, 65), (gx, y), (gx, y + height), 1)
        gy = y + i * height // 5
        py.draw.line(surface, (65, 65, 65), (x, gy), (x + width, gy), 1)

    if len(time_data) < 2:
        return

    start_time = max(0, time_data[-1] - 10)
    scale = peak_energy * 1.1
    baseline = y + height

    def to_points(data):
        pts = []
        for t, e in zip(time_data, data):
            if t < start_time:
                continue
            px = x + ((t - start_time) / 10) * width
            py_pos = baseline - (e / scale) * height
            pts.append((int(px), int(py_pos)))
        return pts

    ke_pts = to_points(KE_data)
    pe_pts = to_points(PE_data)

    if len(pe_pts) > 1:
        py.draw.lines(surface, FORCE_SPRING, False, pe_pts, 2)
    if len(ke_pts) > 1:
        py.draw.lines(surface, (100, 200, 255), False, ke_pts, 2)
    
def main():
    global mass
    global stiffness
    global damping

    py.init()
    screen = py.display.set_mode((W,H))
    title = py.display.set_caption("Horizontal spring simulation.")
    clock = py.time.Clock()

    font_smaller = py.font.SysFont(("Consolas"),13)
    font_small = py.font.SysFont(("Consolas"),16) 
    font_big = py.font.SysFont(("Consolas"),32)

    m_font = font_big.render("m",True,(225, 245, 238))
    m_value = font_small.render(f"{math.ceil(mass)}Kg", True, white)
    equilibrium_text = font_small.render("Equilibrium", True, TEXT_C)
    hint = font_small.render("drag the mass | R reset | F forces | Esc quit", True, TEXT_C)
    spring_formula = font_smaller.render("F = -Kx", True, TEXT_C)

    slider_start = 40
    slider_end = 330
    mass_slider_x = 69
    stiffness_slider_x = 98
    damping_slider_x = 69

    mass_slider = False
    stiffness_slider = False
    damping_slider = False

    running = True
    show_forces = True
    dragging = False
    pos, vel = reset()

    mass_slider_center = (mass_slider_x, H - 155)
    stiffness_slider_center = (stiffness_slider_x, H - 95)
    damping_slider_center = (damping_slider_x, H - 35)

    #graph-data
    time_data = []
    displacement_data = []
    KE_data = []
    PE_data = []
    elapsed_time = 0.0

    slider_len = np.linalg.norm([[40, H - 95] - np.array([330, H - 95])])
    
    while running:
        frame_dt = min(1/30, clock.tick(60) / 1000.0)
        mass_rect = py.Rect(int(pos), HEIGHT - (mass_SIZE // 2), mass_SIZE, mass_SIZE)

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

                    mass = 5.0
                    stiffness = 100.0
                    damping = 2.0
                    mass_slider_x = 69
                    stiffness_slider_x = 98
                    damping_slider_x = 69

                    time_data.clear()
                    displacement_data.clear()
                    KE_data.clear()
                    PE_data.clear()
                    elapsed_time = 0.0

                    mass_slider_center = (mass_slider_x, H - 155)
                    stiffness_slider_center = (stiffness_slider_x, H - 95)
                    damping_slider_center = (damping_slider_x, H - 35)

                elif e.key == py.K_f:

                    show_forces = not show_forces

            elif e.type == py.MOUSEBUTTONDOWN:

                mouse = e.pos

                if np.linalg.norm(mouse - np.array([pos, HEIGHT])) < 110:
                    dragging = True

                elif np.linalg.norm(mouse - np.array([mass_slider_center])) < 20:
                    mass_slider = True

                elif np.linalg.norm([mouse - np.array([stiffness_slider_center])]) < 20:
                    stiffness_slider = True
                    
                elif np.linalg.norm(mouse - np.array([damping_slider_center])) < 20:
                    damping_slider = True

            elif e.type == py.MOUSEBUTTONUP:
                dragging  = False
                mass_slider = False
                stiffness_slider = False
                damping_slider = False

        if mass_slider:
            x, y =  py.mouse.get_pos()
            mass_slider_x = max(slider_start, min(slider_end, x))
            mass_slider_center = (mass_slider_x, mass_slider_center[1])
            changed_len = np.linalg.norm([np.array([mass_slider_center]) - np.array([40, mass_slider_center[1]])])
            scaler = round(changed_len / slider_len, 2)
            mass = max(MIN_mass, min(MAX_mass * scaler, MAX_mass))

        if stiffness_slider:
            x, y = py.mouse.get_pos()
            stiffness_slider_x = max(slider_start, min(slider_end, x))
            stiffness_slider_center =  (stiffness_slider_x, H - 95)
            changed_len = np.linalg.norm(np.array([stiffness_slider_center]) - np.array([40, H - 95]))
            scaler = round(changed_len / slider_len, 2)
            stiffness = max(MIN_stiffness, min(scaler * MAX_stiffness, MAX_stiffness))

        if damping_slider:
            x, y = py.mouse.get_pos()
            damping_slider_x = max(slider_start, min(slider_end, x))
            damping_slider_center = (damping_slider_x, damping_slider_center[1])
            changed_len = np.linalg.norm([np.array([damping_slider_center] -  np.array([40, damping_slider_center[1]]))])
            scaler = round(changed_len / slider_len, 2)
            damping = max(MIN_damping, min(scaler * MAX_damping, MAX_damping))

        #---- energy calculation -----
        stretch = (pos - ANCHOR[0]) - L0
        _, f_spring, f_damping = calculate_forces(pos, vel)
        KE = 0.5 * mass * vel**2
        PE = 0.5 * stiffness * stretch**2

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

            elapsed_time += frame_dt
            time_data.append(elapsed_time)
            displacement_data.append(stretch)
            KE_data.append(KE)
            PE_data.append(PE)

            while time_data and time_data[0] < elapsed_time - 10:
                time_data.pop(0)
                displacement_data.pop(0)

            while (KE_data and KE_data[0] < elapsed_time - 10) and (PE_data and PE_data[0] < elapsed_time - 10):
                KE_data.pop(0)
                PE_data.pop(0)


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

        rotated_equilibrium_text = py.transform.rotate(equilibrium_text, 90)
        screen.blit(rotated_equilibrium_text, (EQ_X - 20 , 220))


        #---- draw pivot point ----
        py.draw.circle(screen, (44,44,42), ANCHOR, 2)
        py.draw.circle(screen, (44,44,42), ANCHOR, 10, 3)

        #---- spring ----
        color = spring_color(pos)
        pts, mid_point = spring_points(ANCHOR, pos)
        py.draw.lines(screen, SPRING_OUTLINE, False, pts, 8)
        py.draw.lines(screen, color, False, pts, 5)
        py.draw.aalines(screen, lerp_color(color, (255,255,255), 0.45), False, pts)

        #---- shadow ----
        shadow = py.Surface((mass_SIZE + 20, 16), py.SRCALPHA)
        py.draw.ellipse(shadow, (0,0,0,90), shadow.get_rect())
        screen.blit(shadow, (pos - 7, HEIGHT + 45))

        #---- mass ----
        #pygame.draw.rect(surface, color, (x, y, width, height), border_radius=0)
        py.draw.rect(screen, (29,158,117), (pos, HEIGHT - 49, 100, 100), border_radius=10)
        py.draw.rect(screen, (32,86,69), (pos, HEIGHT - 49, 100, 100), 5, border_radius=10)
        start_pos = pos + 15, HEIGHT - 35
        end_pos =  pos + 85, HEIGHT - 35
        border = py.Surface((W, H), py.SRCALPHA)
        upper_left_border = py.Surface((W,H), py.SRCALPHA)
        upper_right_border = py.Surface((W,H), py.SRCALPHA)
        fade_surface = py.Surface((W,H), py.SRCALPHA)
        py.draw.line(fade_surface, (255,255,255,75), start_pos, end_pos, 5)
        py.draw.circle(fade_surface, (255,255,255,75), start_pos, 2)
        py.draw.circle(fade_surface, (255,255,255,75), end_pos, 2)
        py.draw.rect(border, (0,0,0,85), (0, 0, 260, 180), border_radius=20)
        screen.blit(fade_surface, (0,0))
        screen.blit(border, (W - 300, H - 210))

        #---- borders -----
        py.draw.rect(border,(0,0,0,85), (0,0, 350, 190), border_radius=20)
        screen.blit(border, (20, H - 200))

        #------ displacement vs time ------
        dt_graph_x = 440
        dt_graph_y = 40
        py.draw.rect(upper_left_border, (255,255,255,10), (0, 0, 350, 160), border_radius=20)
        screen.blit(upper_left_border, (420, 20))
        py.draw.line(screen, (TEXT_C), (dt_graph_x, 150), (dt_graph_x + 305, 150), 2)
        py.draw.line(screen, (TEXT_C), (dt_graph_x + 10, 160), (dt_graph_x + 10, dt_graph_y),2)
        displacement_text = font_smaller.render("Displacement(x)", True, TEXT_C)
        rotated_displacement_text = py.transform.rotate(displacement_text, 90)
        screen.blit(rotated_displacement_text, (dt_graph_x - 5, 40),)
        time_text = font_smaller.render("Time(t)", True, TEXT_C)
        screen.blit(time_text, (dt_graph_x + 120, 155))

        draw_displacement_graph(
            screen,
            (455, 40, 300, 105),
            time_data, 
            displacement_data
        )


        py.draw.rect(upper_right_border, (225,225,225,10), (0,0, 350, 160), border_radius=20)
        screen.blit(upper_right_border, (20 , 20))
        py.draw.line(screen, (TEXT_C), (30, 150), (350, 150), 2)
        py.draw.line(screen, (TEXT_C), (45, 170), (45, 30), 2)
        time_text_e = font_smaller.render("Time(t)", True, TEXT_C)
        energy_text = font_smaller.render("Energy", True, TEXT_C)
        rotated_energy_text = py.transform.rotate(energy_text, 90)
        screen.blit(rotated_energy_text, (30, 65))
        screen.blit(time_text_e, (350 // 2 - 10, 155))

        peak_energy = 1.0

        peak_energy = max(peak_energy, KE + PE)

        draw_energy_graph(
            screen,
            (50, 40, 300, 105),
            time_data, 
            KE_data,
            PE_data,
            peak_energy
        )

        #---- tuning slider ----
        screen.blit(font_small.render(f"mass:{mass:5.2f} kg", True, TEXT_C), (40, H - 190))
        py.draw.line(screen, (TEXT_C), (slider_start, H - 155), (slider_end, H - 155), 2)
        py.draw.circle(screen, (GROUND_EDGE), mass_slider_center, 8)
        py.draw.circle(screen, (TEXT_C), mass_slider_center, 5)

        screen.blit(font_small.render(f"stiffness: {stiffness:5.2f} ", True, TEXT_C), (40, H - 130))
        py.draw.line(screen, (TEXT_C), (40, H - 95), (330, H - 95), 2)
        py.draw.circle(screen, (GROUND_EDGE), stiffness_slider_center, 8)
        py.draw.circle(screen, (TEXT_C), stiffness_slider_center, 5)

        screen.blit(font_small.render(f"damping: {damping:5.2f} ", True, TEXT_C), (40, H - 70))
        py.draw.line(screen, (TEXT_C), (40, H - 35), (330, H - 35), 2)
        py.draw.circle(screen, (GROUND_EDGE), damping_slider_center, 8)
        py.draw.circle(screen, (TEXT_C), damping_slider_center, 5)

        #---- show-forces ----
        if show_forces:
            center_x = mass_rect.centerx
            top = mass_rect.y
            arrow(screen, FORCE_SPRING, (center_x, top - 20), max(-160,min(160, f_spring * 0.05)))
            arrow(screen, FORCE_DAMP, (center_x, top - 38), max(-160,min(160, f_damping * 0.05)))

        #---- texts ----
        screen.blit(m_font, (pos + 40, HEIGHT - 13))
        screen.blit(m_value, (pos + 35, HEIGHT + 20))
        screen.blit(hint, (40, H - 230))
        info_list = [
            (f"x    {stretch:+9.5f} pxls", TEXT_C),
            (f"v    {vel:+9.5f} pxls/s",TEXT_C),
            (f"F_s  {f_spring:+9.5f}", FORCE_SPRING),
            (f"F_d  {f_damping:+9.5f}", FORCE_DAMP),
            (f"KE   {KE:9,.5f}", TEXT_C),
            (f"PE   {PE:9,.5f}", TEXT_C)
        ]
        for i, (value, color) in enumerate(info_list):
            screen.blit(font_small.render(value, True, color), (W - 260, H - 190 + i * 25))

        screen.blit(spring_formula, (mid_point[0] - 20, mid_point[1] - 40))
        py.display.update()
    py.quit()


if __name__ == "__main__":
    main()