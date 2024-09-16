import numpy as np
import pygame

from globals import *


class BezierCurve:

    # p = points
    def __init__(self, p, handle_radius):
        self.p = p
        self.handle_radius = handle_radius

    def lerp(self, p0, p1, t):
        assert 0 <= t <= 1
        return (1 - t) * p0 + t * p1

    def de_casteljau_algorithm(self, t):

        # linear interpolation all the way down
        curr_points = self.p

        while len(curr_points) > 1:

            new_points = []

            for i in range(len(curr_points) - 1):
                new_point = self.lerp(curr_points[i], curr_points[i + 1], t)
                new_points.append(new_point)

            curr_points = new_points

        return curr_points[0]

    def eval(self, t):
        assert 0 <= t <= 1
        return self.de_casteljau_algorithm(t)

    def get_color(self, i):

        # the knots should be red, the handles should be blue
        if len(self.p) == 4:
            return PASTEL_RED if i == 0 or i == 3 else PASTEL_BLUE
        else:
            return BLACK

    def draw_handles(self, canvas, camera, radius, color, stroke_weight):

        for i in range(0, len(self.p) - 1, 2):

            p1 = self.p[i] + np.array([-camera.camera_x, -camera.camera_y])
            p2 = self.p[i + 1] + np.array([-camera.camera_x, -camera.camera_y])

            pygame.draw.circle(canvas, color=self.get_color(i), center=p1, radius=radius, width=stroke_weight)
            pygame.draw.circle(canvas, color=self.get_color(i + 1), center=p2, radius=radius, width=stroke_weight)
            pygame.draw.line(canvas, color, p1, p2, width=(stroke_weight // 2))

    def draw(self, canvas, camera, color=BLACK, stroke_weight=5, n_samples=64):

        sampled_points = []

        for i in range(n_samples):

            t = (1 / n_samples) * i
            sampled_points.append(self.eval(t))

        for i, p in enumerate(sampled_points):
            sampled_points[i] = (p + np.array([-camera.camera_x, -camera.camera_y]))

        for i in range(n_samples - 1):

            pygame.draw.line(canvas, color, sampled_points[i], sampled_points[i + 1], width=stroke_weight)

        # draw the UI elements
        self.draw_handles(canvas, camera, radius=self.handle_radius, color=color, stroke_weight=stroke_weight)




