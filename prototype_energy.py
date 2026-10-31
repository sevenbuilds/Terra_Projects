import pygame as py
from sys import exit

W, H = 800, 600
# rect
x = 50
y = 50
width = W - (x * 2) # margin
height = H - (y * 2) # margin
right = W - x
bottom = H - y

#colors:
Ruby_Red = (212, 106, 123)
Sea_green = (126, 206, 173)
white = (255,255,255)
black = (0,0,0)

GROUND_C = (58, 58, 56)
GROUND_EDGE = (136, 135, 128)
SPRING_OUTLINE = (20, 20, 22)
TEXT_C = (180, 178, 169)
BG = (25,25,25)

def draw_energy_graph(surface, rect, time_data, KE_data, PE_data, peak_energy):

    x, y, width, height = rect

    # grid lines
    
    for i in range(1,5):
        gy = y + (i * height // 5)
        py.draw.line(surface, (TEXT_C), (x , gy), (right, gy), 1)
        gx = x + (i * width // 5)
        py.draw.line(surface, (TEXT_C), (gx , y), (gx, bottom), 1)

    if len(time_data) < 2:
        return

    #scaler used because if we used peak energy directly at max energy the graph will touch the y 
    # and since we want the graph to breathe we keep 10% of the space free
    scaler =  1.1 * peak_energy

    def convert_into_points(data):
        pts = []
        for t, e in zip(time_data, data):
            px_pos = x + ( t / 10) * width
            py_pos = bottom - (e / scaler) * height
            pts.append((int(px_pos), int(py_pos)))
        return pts

    KE_pts = convert_into_points(KE_data)
    PE_pts = convert_into_points(PE_data)

    if len(KE_pts) > 1:
        py.draw.lines(surface, (Ruby_Red), False, KE_pts, 2)
    if len(PE_pts) > 1:
        py.draw.lines(surface, (Sea_green), False, PE_pts, 2)


def main():
    # data
    time_data = [0,   1,  2,  3,  4,  5,  6,  7,  8,  9, 10]
    PE_data   = [100, 10, 45,  8, 22,  4, 10,  2,  4,  1,  2]
    KE_data   = [0,   60,  5, 27,  3, 14,  2,  7,  2,  3,  1] 

    # border:

    py.init()
    title = py.display.set_caption("Energy vs Time Graph.")
    screen = py.display.set_mode((W,H))
    clock = py.time.Clock()
    small_font = py.font.SysFont("Consolas", 16)
    big_font = py.font.SysFont("Consolas", 32)
    rect = x, y, width, height


    running = True
    while running:
        frame_dt = max(1/30, clock.tick(60)/1000.0)
        for e in py.event.get():
            if e.type == py.QUIT or (e.type == py.KEYDOWN and e.key == py.K_ESCAPE):
                exit()
                running = False
                py.quit()

        #--- energy ---


        #--- rendering part-----
        screen.fill((BG))

        # x-axis
        py.draw.circle(screen, (TEXT_C), (right, bottom), 2)
        py.draw.line(screen, (TEXT_C), (x, bottom), (right, bottom), 3)

        # y-axis
        py.draw.circle(screen, (TEXT_C), (x,y), 2)
        py.draw.line(screen, (TEXT_C), (x , bottom), (x, y), 3)

        # graph coordinates

        peak_energy = max(0, max(PE_data), max(KE_data))

        draw_energy_graph(
            screen,
            rect,
            time_data,
            KE_data,
            PE_data,
            peak_energy
        )

        #--- text ----
        time = big_font.render("Time(t)", True, (TEXT_C))
        time_coordinate = x + (width / 2) - (time.get_width() / 2)
        screen.blit(time, (time_coordinate, bottom + 10))

        energy = big_font.render("Energy", True, (TEXT_C))
        rotated_energy = py.transform.rotate(energy, 90)
        energy_coordinate = y + (height / 2) - (rotated_energy.get_height() / 2)
        screen.blit(rotated_energy, (x - 35, energy_coordinate))

        Kinetic_energy = small_font.render("Kinectic Energy: ", True, (TEXT_C))
        screen.blit(Kinetic_energy, (x, y - 30))
        color_x = x + Kinetic_energy.get_width()
        color_y = y - 30

        py.draw.rect(screen, (Ruby_Red), (color_x, color_y, 20, 20), border_radius= 3)

        Potential_energy = small_font.render("Potential Energy: ", True, (TEXT_C))
        screen.blit(Potential_energy, (color_x + 30, color_y))

        py.draw.rect(screen, (Sea_green), (color_x + Potential_energy.get_width() + 30, color_y, 20, 20), border_radius=3)


        py.display.update()
    py.quit()

if __name__ == "__main__":
    main()