from venv import create

import pygame
import sys
import numpy as np

from bezier import BezierCurve
from bezier_spline import CubicBezierSpline
from camera import Camera
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

millis_at_last_click = None

draw_points_on_bezier_curves = True
draw_normals_on_bezier_curves = False

camera = Camera()

middle_mouse_button_pressed = False

def get_random_offset():

    random_angle = np.random.randint(angle_range[0], angle_range[1])
    random_angle_rad = random_angle * (2 * np.pi / 360)

    return initial_handle_distance * np.array([np.cos(random_angle_rad), np.sin(random_angle_rad)])

def create_color_picker_popup(screen_width = WIDTH, screen_height = HEIGHT):
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    OVERLAY = (0, 0, 0, 0)

    # Popup properties
    popup_width, popup_height = 350, 250
    popup_x = (screen_width - popup_width) // 2
    popup_y = (screen_height - popup_height) // 2
    border_thickness = 2

    # Slider properties
    slider_width = 200
    slider_height = 20
    slider_x = popup_x + (popup_width - slider_width) // 2
    slider_y_start = popup_y + 30
    slider_y_gap = 40

    # Current color values
    red, green, blue = 128, 128, 128

    # Font
    font = pygame.font.Font(None, 24)

    # Create overlay surface
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill(OVERLAY)

    # Create popup surface
    popup = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
    popup.fill((255, 255, 255, 220))  # Semi-transparent white

    def draw_slider(y, value, color):
        pygame.draw.rect(popup, BLACK, (slider_x - popup_x, y - popup_y, slider_width, slider_height), 2)
        pygame.draw.rect(popup, color + (255,), (slider_x - popup_x, y - popup_y, int(value / 255 * slider_width), slider_height))

    def get_slider_value(mouse_x, slider_x):
        return max(0, min(255, int((mouse_x - slider_x) / slider_width * 255)))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if slider_x <= mouse_x <= slider_x + slider_width:
                    if slider_y_start <= mouse_y <= slider_y_start + slider_height:
                        red = get_slider_value(mouse_x, slider_x)
                    elif slider_y_start + slider_y_gap <= mouse_y <= slider_y_start + slider_y_gap + slider_height:
                        green = get_slider_value(mouse_x, slider_x)
                    elif slider_y_start + 2 * slider_y_gap <= mouse_y <= slider_y_start + 2 * slider_y_gap + slider_height:
                        blue = get_slider_value(mouse_x, slider_x)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return (red, green, blue)
                if event.key == pygame.K_ESCAPE:
                    return None

        # Store the current screen state
        background = screen.copy()

        # Draw overlay
        background.blit(overlay, (0, 0))

        # Update popup
        popup.fill((255, 255, 255, 220))  # Semi-transparent white

        # Draw sliders
        draw_slider(slider_y_start, red, (red, 0, 0))
        draw_slider(slider_y_start + slider_y_gap, green, (0, green, 0))
        draw_slider(slider_y_start + 2 * slider_y_gap, blue, (0, 0, blue))

        # Draw labels
        popup.blit(font.render(f"R: {red}", True, BLACK), (slider_x - popup_x + slider_width + 10, slider_y_start - popup_y))
        popup.blit(font.render(f"G: {green}", True, BLACK), (slider_x - popup_x + slider_width + 10, slider_y_start - popup_y + slider_y_gap))
        popup.blit(font.render(f"B: {blue}", True, BLACK), (slider_x - popup_x + slider_width + 10, slider_y_start - popup_y + 2 * slider_y_gap))

        # Draw color preview
        pygame.draw.rect(popup, (red, green, blue, 255), (slider_x - popup_x, slider_y_start - popup_y + 3 * slider_y_gap, slider_width, slider_height * 2))

        # Draw instructions
        instructions = font.render("Enter to confirm, Esc to cancel", True, BLACK)
        popup.blit(instructions, ((popup_width - instructions.get_width()) // 2, popup_height - 30))

        # Draw popup on background
        background.blit(popup, (popup_x, popup_y))

        pygame.draw.rect(background, BLACK, (popup_x - border_thickness, popup_y - border_thickness,
                                             popup_width + 2 * border_thickness, popup_height + 2 * border_thickness),
                         border_thickness)

        # Update the screen
        screen.blit(background, (0, 0))
        pygame.display.flip()

    return None

def draw_tool_indicator():

    # Set up font
    font = pygame.font.Font(None, 36)  # None uses default font, 36 is the size

    # Determine which letter to draw
    if current_tool == Tool.TRANSLATE:
        text = "T"
    elif current_tool == Tool.DRAW:
        text = "D"
    elif current_tool == Tool.CLOSE:
        text = "C"
    elif current_tool == Tool.FILL:
        text = "F"
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

def create_popup(message, font_size=32):


    # Create a surface for the popup
    popup_width, popup_height = 300, 200
    popup_surface = pygame.Surface((popup_width, popup_height))
    popup_surface.fill(GRAY)

    # Create font
    font = pygame.font.Font(None, font_size)

    # Render message
    message_surface = font.render(message, True, BLACK)
    message_rect = message_surface.get_rect(center=(popup_width // 2, popup_height // 2 - 30))

    # Create buttons
    button_width, button_height = 80, 40
    yes_button = pygame.Rect(popup_width // 4 - button_width // 2, popup_height - 60, button_width, button_height)
    no_button = pygame.Rect(3 * popup_width // 4 - button_width // 2, popup_height - 60, button_width, button_height)

    # Draw everything on the popup surface
    popup_surface.blit(message_surface, message_rect)
    pygame.draw.rect(popup_surface, GREEN, yes_button)
    pygame.draw.rect(popup_surface, RED, no_button)

    yes_text = font.render("Yes", True, BLACK)
    no_text = font.render("No", True, BLACK)
    popup_surface.blit(yes_text, yes_text.get_rect(center=yes_button.center))
    popup_surface.blit(no_text, no_text.get_rect(center=no_button.center))

    # Get the position to center the popup on the screen
    screen_center = screen.get_rect().center
    popup_pos = (screen_center[0] - popup_width // 2, screen_center[1] - popup_height // 2)

    # Main loop for the popup
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                relative_mouse_pos = (mouse_pos[0] - popup_pos[0], mouse_pos[1] - popup_pos[1])
                if yes_button.collidepoint(relative_mouse_pos):
                    return True
                elif no_button.collidepoint(relative_mouse_pos):
                    return False

        # Draw the popup on the main screen
        screen.blit(popup_surface, popup_pos)
        pygame.display.flip()

    return None

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

            if event.button == 2:
                middle_mouse_button_pressed = True

            if event.button == 1:  # Left mouse button

                if current_tool == Tool.TRANSLATE:
                    # select existing
                    for spline in splines:

                        potential_handle_idx = spline.get_handle_idx(camera, mouse_x, mouse_y)

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
                        selected_spline.add_new_points([
                            np.array([mouse_x, mouse_y]) + offset_1,
                            np.array([mouse_x, mouse_y]) + offset_2,
                            np.array([mouse_x, mouse_y])
                        ])

                        # select the last two handles to move them
                        selected_handle_idx = [-2, -1]

                        selected_spline.update_bezier_curves_from_points()

                elif current_tool == Tool.CLOSE:

                    found_selection = False

                    for spline in splines:

                        potential_handle_idx = spline.get_handle_idx(camera, mouse_x, mouse_y)

                        if potential_handle_idx is not None:
                            found_selection = True
                            selected_spline = spline
                            selected_handle_idx = [potential_handle_idx]
                            break

                    # deselect currently selected because clicked in empty region
                    if not found_selection:
                        selected_spline = None
                        selected_handle_idx = None

                elif current_tool == Tool.FILL:

                    # TODO: only open if inside the closed curve

                    color = create_color_picker_popup()

                    point = np.array([mouse_x, mouse_y])

                    if color is not None:

                        for spline in splines:

                            if spline.is_point_inside(point):

                                spline.fill_color = color
                                break


        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 2:
                middle_mouse_button_pressed = False

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

            elif event.key == pygame.K_f:
                current_tool = Tool.FILL
                selected_spline = None
                selected_handle_idx = None

            elif event.key == pygame.K_n:
                # normal drawing can be toggled with N
                draw_normals_on_bezier_curves = not draw_normals_on_bezier_curves

            elif event.key == pygame.K_c:

                if current_tool != Tool.CLOSE:
                    current_tool = Tool.CLOSE
                    selected_spline = None
                    selected_handle_idx = None

                elif selected_spline is not None and not selected_spline.is_closed:

                    answer = create_popup("Close the curve?")

                    if answer:
                        selected_spline.close()

                    selected_spline = None
                    selected_handle_idx = None

                    current_tool = Tool.TRANSLATE

    # Drawing
    screen.fill(WHITE)

    mouse_x, mouse_y = pygame.mouse.get_pos()

    mouse_dx = mouse_x - last_mouse_x
    mouse_dy = mouse_y - last_mouse_y

    # camera movement
    if middle_mouse_button_pressed:
        # camera moves opposite to mouse
        camera.move(-mouse_dx, -mouse_dy)

    if selected_spline is not None:

        if current_tool == Tool.TRANSLATE or current_tool == Tool.DRAW:
            for idx in selected_handle_idx:
                selected_spline.p[idx] += np.array([mouse_dx, mouse_dy])

    # Add your drawing code here
    for spline in splines:
        spline.draw(screen, camera, color=(BRIGHT_ORANGE if current_tool == Tool.CLOSE and spline == selected_spline else BLACK))

    for spline in splines:

        if spline.fill_color is not None:
            spline.draw_interior(screen, camera)

    if draw_points_on_bezier_curves:

        all_points = []

        all_normals = []

        for spline in splines:
            all_points += spline.get_boundary_points(n_samples_per_curve=10)

            if draw_normals_on_bezier_curves:
                all_normals += spline.get_normals()

        for i, p in enumerate(all_points):

            p = p + np.array([-camera.camera_x, -camera.camera_y])

            pygame.draw.circle(screen, RED, center=p, radius=4)

            if draw_normals_on_bezier_curves:
                line_length = 50
                pygame.draw.line(screen, RED, p, p + line_length * all_normals[i])

    draw_tool_indicator()

    # Update the display
    pygame.display.flip()

    last_mouse_x = mouse_x
    last_mouse_y = mouse_y

# Quit Pygame
pygame.quit()
sys.exit()