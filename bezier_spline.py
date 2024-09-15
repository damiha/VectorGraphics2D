from ctypes.wintypes import HANDLE

from globals import *
from bezier import BezierCurve
import pygame
import numpy as np

class CubicBezierSpline:

    def __init__(self, p, handle_radius=HANDLE_RADIUS):
        # radius for the knots (UI elements)
        self.handle_radius = handle_radius
        self.p = p

        # a level of indirection to allow closed curves?
        # there may be more indices than points
        self.p_indices = [i for i in range(len(self.p))]

        self.bezier_curves = []

        self.update_bezier_curves_from_points()

        self.is_closed = False

    def add_new_points(self, new_points):

        # extend the number of indices as well
        n_curr_points = len(self.p)

        self.p_indices += [n_curr_points + i for i in range(len(new_points))]

        self.p += new_points

    def update_bezier_curves_from_points(self):

        self.bezier_curves = []

        for i in range(0, len(self.p_indices), 3):

            points_for_bezier = [self.p[j] for j in self.p_indices[i:i+4]]

            # take the next four points
            self.bezier_curves.append(BezierCurve(points_for_bezier, self.handle_radius))

    def close(self):

        # adds two new points
        self.add_new_points([self.p[-1] + np.array([50, 50]), self.p[0] + np.array([50, 50])])

        self.p_indices += [self.p_indices[0]]

        self.is_closed = True

        self.update_bezier_curves_from_points()

    def get_boundary_points(self):
        pass

    def is_point_inside(self, point):

        pass

    def get_handle_idx(self, mouse_x, mouse_y):

        for i, point in enumerate(self.p):

            if np.linalg.norm(point - np.array([mouse_x, mouse_y])) < self.handle_radius:

                return i

        return None

    def draw(self, canvas, color=BLACK, stroke_weight=5, n_samples_per_segment=64):

        for bezier_curve in self.bezier_curves:
            bezier_curve.draw(canvas=canvas, color=color, stroke_weight=stroke_weight, n_samples=n_samples_per_segment)
