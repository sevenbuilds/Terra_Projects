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

# colors
TEXT_C = (180, 178, 169)
LIGHT_TEXT_C = (205, 203, 195)
BG = (25,25,25)
#colors:
Ruby_Red = (212, 106, 123)
Sea_green = (126, 206, 173)
white = (255,255,255)
black = (0,0,0)

def draw_displacement_graph(surface, rect, time_data, displacement_data, peak_displacement):
    x, y, width, height = rect

    # draw grids

    for i in range(1,5):
        gy = y + (i * height // 5)
        py.draw.line(surface, (LIGHT_TEXT_C), (x , gy), (right, gy), 1)
        gx = x + (i * width // 5)
        py.draw.line(surface, (LIGHT_TEXT_C), (gx , y), (gx, bottom), 1)

    # mid_point
    mid_point = bottom - height / 2
    py.draw.line(surface, (TEXT_C), (x ,bottom - height / 2), (right, bottom - height / 2), 1)

    scaler = 1.1 * peak_displacement

    if len(time_data) < 2:
        return

    def convert_into_points(data):
        pts = []
        for t, d  in zip(time_data, data):
            px_pos = x + (t / 10) * width
            py_pos = mid_point - (d / scaler) * (height / 2)
            pts.append((int(px_pos),int(py_pos)))
        return pts
    
    displacement_pts = convert_into_points(displacement_data)

    if len(displacement_data) > 1:
        for i in range(len(displacement_pts) - 1):
            p1 = displacement_pts[i]
            p2 = displacement_pts[i + 1]

            avg_y = (p1[1] + p2[1]) / 2

            color = Sea_green if avg_y > mid_point else Ruby_Red

            py.draw.line(surface, color, p1, p2, 2)



def main():
    py.init()
    title = py.display.set_caption("Displacement vs Time Graph.")
    clock = py.time.Clock()
    screen = py.display.set_mode((W,H))

    small_font = py.font.SysFont("Consolas", 16)
    big_font = py.font.SysFont("Consolas", 32)

    time_data = [
        0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5,
        5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10
        ]

    disp_data = [
        100, 64.6, 5.5, -43.2, -60.0, -43.9, -10.0, 21.4, 35.3, 29.0, 9.9,
        -9.7, -20.3, -18.7, -8.3, 3.9, 11.4, 11.7, 6.3, -1.0, -6.2
        ]

    running = True
    while running:
        frame_dt = min(1/30, clock.tick(60) / 1000.0)
        for e in py.event.get():
            if e.type == py.QUIT or (e.type == py.KEYDOWN and e.key == py.K_ESCAPE):
                exit()
                running = False
                py.quit()

        #--- render ----
        screen.fill((BG))

        # x-axis
        py.draw.circle(screen, (TEXT_C), (right, bottom), 2)
        py.draw.line(screen, (TEXT_C), (x, bottom), (right, bottom), 3)
        
        # y-axis
        py.draw.circle(screen, (TEXT_C), (x,y), 2)
        py.draw.line(screen, (TEXT_C), (x , bottom), (x, y), 3)

        # draw graph

        rect = x, y, width, height
        peak_displacement = abs(max(disp_data, key=abs))

        draw_displacement_graph(
            screen,
            rect,
            time_data,
            disp_data,
            peak_displacement
        )

        #--- text ----
        time = big_font.render("Time(t)", True, (TEXT_C))
        time_coordinate = x + (width / 2) - (time.get_width() / 2)
        screen.blit(time, (time_coordinate, bottom + 10))
        
        energy = big_font.render("Displacement(x)", True, (TEXT_C))
        rotated_energy = py.transform.rotate(energy, 90)
        energy_coordinate = y + (height / 2) - (rotated_energy.get_height() / 2)
        screen.blit(rotated_energy, (x - 35, energy_coordinate))
        
        Displacement_text = small_font.render("Displacement(x): ", True, (TEXT_C))
        screen.blit(Displacement_text, (x, y - 30))

        py.display.update()
    py.quit()

if __name__  == "__main__":
    main()
