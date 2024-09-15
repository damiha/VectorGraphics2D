import pygame
import sys
import numpy as np

from bezier import BezierCurve
from bezier_spline import CubicBezierSpline
from globals import *

# Initialize Pygame
pygame.init()

# Set up the display

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vector Graphics 2D")

splines = []

last_mouse_x = 0
last_mouse_y = 0

mouse_dx = 0
mouse_dy = 0

dragging = False

selected_spline = None
selected_handle_idx = None

initial_handle_distance = 100
angle_range = [20, 60]

current_tool = Tool.TRANSLATE

def get_random_offset():

    random_angle = np.random.randint(angle_range[0], angle_range[1])
    random_angle_rad = random_angle * (2 * np.pi / 360)

    return initial_handle_distance * np.array([np.cos(random_angle_rad), np.sin(random_angle_rad)])

def draw_tool_indicator():

    # Set up font
    font = pygame.font.Font(None, 36)  # None uses default font, 36 is the size

    # Determine which letter to draw
    if current_tool == Tool.TRANSLATE:
        text = "T"
    elif current_tool == Tool.DRAW:
        text = "D"
    else:
        raise NotImplementedError

    # Render the text
    text_surface = font.render(text, True, WHITE, BLACK)

    # Get the rect of the text surface and position it
    text_rect = text_surface.get_rect()
    text_rect.topleft = (10, 10)  # 10 pixels from the top and left edges

    # Draw a background rectangle
    pygame.draw.rect(screen, BLACK, (5, 5, 30, 30))

    # Blit the text onto the screen
    screen.blit(text_surface, text_rect)

def create_new_spline():
    pass

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = event.pos
            last_mouse_x, last_mouse_y = mouse_x, mouse_y

            if event.button == 1:  # Left mouse button

                if current_tool == Tool.TRANSLATE:
                    # select existing
                    for spline in splines:

                        potential_handle_idx = spline.get_handle_idx(mouse_x, mouse_y)

                        if potential_handle_idx is not None:
                            selected_spline = spline
                            selected_handle_idx = [potential_handle_idx]
                            break

                elif current_tool == Tool.DRAW:

                    offset_1 = get_random_offset()
                    offset_2 = get_random_offset()

                    if selected_spline is None:

                        new_spline = CubicBezierSpline([
                            np.array([mouse_x, mouse_y]), # position just clicked
                            np.array([mouse_x, mouse_y]) + offset_1, # another handle for position just clicked
                            np.array([mouse_x, mouse_y]) + offset_2,  # position just clicked
                            np.array([mouse_x, mouse_y])
                        ])

                        selected_spline = new_spline
                        selected_handle_idx = [2, 3] # move both 3rd and 4th handle at the same time

                        splines.append(new_spline)

                    else:

                        # just append two new points and switch to them
                        selected_spline.p += [
                            np.array([mouse_x, mouse_y]) + offset_1,
                            np.array([mouse_x, mouse_y]) + offset_2,
                            np.array([mouse_x, mouse_y])
                        ]

                        # select the last two handles to move them
                        selected_handle_idx = [-2, -1]

                        selected_spline.update_bezier_curves_from_points()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:

                if current_tool == Tool.TRANSLATE:
                    selected_spline = None
                    selected_handle_idx = None

                elif current_tool == Tool.DRAW:
                    pass

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:
                current_tool = Tool.TRANSLATE

                selected_spline = None
                selected_handle_idx = None

            elif event.key == pygame.K_d:
                current_tool = Tool.DRAW

                selected_spline = None
                selected_handle_idx = None

    # Drawing
    screen.fill(WHITE)

    mouse_x, mouse_y = pygame.mouse.get_pos()

    mouse_dx = mouse_x - last_mouse_x
    mouse_dy = mouse_y - last_mouse_y

    if selected_spline is not None:

        for idx in selected_handle_idx:
            selected_spline.p[idx] += np.array([mouse_dx, mouse_dy])

    # Add your drawing code here
    for spline in splines:
        spline.draw(screen)

    draw_tool_indicator()

    # Update the display
    pygame.display.flip()

    last_mouse_x = mouse_x
    last_mouse_y = mouse_y

# Quit Pygame
pygame.quit()
sys.exit()