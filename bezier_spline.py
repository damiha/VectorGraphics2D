
from globals import *
from bezier import BezierCurve
import pygame
import numpy as np

class CubicBezierSpline:

    def __init__(self, p, handle_radius=10):
        # radius for the knots (UI elements)
        self.handle_radius = handle_radius
        self.p = p

        self.bezier_curves = []

        self.update_bezier_curves_from_points()

    def update_bezier_curves_from_points(self):
        for i in range(0, len(self.p), 3):

            # take the next four points
            self.bezier_curves.append(BezierCurve(self.p[i:i+4], self.handle_radius))

    def get_handle_idx(self, mouse_x, mouse_y):

        for i, point in enumerate(self.p):

            if np.linalg.norm(point - np.array([mouse_x, mouse_y])) < self.handle_radius:

                return i

        return None

    def draw(self, canvas, color=BLACK, stroke_weight=5, n_samples_per_segment=64):

        for bezier_curve in self.bezier_curves:
            bezier_curve.draw(canvas=canvas, color=color, stroke_weight=stroke_weight, n_samples=n_samples_per_segment)
