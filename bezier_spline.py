from ctypes.wintypes import HANDLE
from ssl import cert_time_to_seconds

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

        self.fill_color = None

        # links to ensure C1 continuity at certain points (user defined)
        # those are tuples
        self.links = []

    def find_neighboring_handle(self, handle_idx):

        # we know its not 0 (knot) so it must be 1 or 2 mod 3
        if handle_idx % 3 == 1:
            # first handle -> get left
            if handle_idx > 3:
                return handle_idx - 2

            elif handle_idx == 1 and self.is_closed:
                return -1

        elif handle_idx % 3 == 2:

            if handle_idx < len(self.p) - 2:
                return handle_idx + 2

            elif handle_idx == len(self.p) - 2 and self.is_closed:
                return 0

        return None

    def belongs_to_handle(self, handle_idx):
        return handle_idx % 3 != 0

    # expects a tuple
    def link(self, link):
        self.links.append(link)

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

    def get_boundary_points(self, n_samples_per_curve=10):

        boundary_points = []

        for bezier_curve in self.bezier_curves:

            boundary_points += [bezier_curve.eval(i * (1.0 / n_samples_per_curve)) for i in range(n_samples_per_curve)]

        return boundary_points

    def get_center_of_curve(self):

        boundary_points = self.get_boundary_points()

        center_of_curve = np.array([0, 0], dtype=float)

        for p in boundary_points:
            center_of_curve += p

        center_of_curve /= len(boundary_points)

        return center_of_curve

    def get_normals(self):

        boundary_points = self.get_boundary_points()

        center_of_curve = self.get_center_of_curve()

        n = len(boundary_points)

        normals = []

        for i in range(n):
            p1 = boundary_points[i]
            p2 = boundary_points[(i + 1) % n]

            tangent = p2 - p1

            normal = np.array([-tangent[1], tangent[0]])

            if np.linalg.norm(normal) == 0:
                normals.append(np.array([0, 0]))
                continue

            normal /= np.linalg.norm(normal)

            to_center = center_of_curve - p1

            if np.dot(normal, to_center) > 0:
                # that would mean center is outside?
                normal = -normal

            normals.append(normal)

        return normals


    def is_point_inside(self, point):

        if not self.is_closed:
            return False

        boundary_points = self.get_boundary_points()

        normals = self.get_normals()

        inside_votes = 0

        for i, normal in enumerate(normals):

            boundary_to_point = point - boundary_points[i]

            if np.dot(boundary_to_point, normal) <= 0:
                inside_votes += 1

        # majority vote (some normals between splines cannot be trusted to point away from the interior)
        return inside_votes > (0.8 * len(normals))

    def get_handle_idx(self, camera, mouse_x, mouse_y):

        # don't move mouse, move points to mouse
        mouse_point = np.array([mouse_x, mouse_y])

        for i, point in enumerate(self.p):

            if np.linalg.norm(camera.transform_point(point) - mouse_point) < self.handle_radius:

                return i

        return None

    def enforce_links(self, selected):

        for (link_source, link_target) in self.links:

            # skip because currently moved
            if selected is not None and selected == link_target:
                continue

            knot_inbetween = int((link_target + link_source) / 2)

            origin_mirror = self.p[knot_inbetween]

            to_mirror = origin_mirror - self.p[link_source]

            self.p[link_target] = origin_mirror + to_mirror

        self.update_bezier_curves_from_points()

    def draw(self, canvas, camera, is_view_mode, color=BLACK, stroke_weight=5, n_samples_per_segment=64):

        for bezier_curve in self.bezier_curves:
            bezier_curve.draw(camera=camera, canvas=canvas, is_view_mode=is_view_mode, color=color, stroke_weight=stroke_weight, n_samples=n_samples_per_segment)

    def draw_interior(self, canvas, camera, n_samples_per_segment=64):

        all_points = self.get_boundary_points(n_samples_per_segment)

        for i, p in enumerate(all_points):
            all_points[i] = camera.transform_point(p)

        pygame.draw.polygon(canvas, color=self.fill_color, points=all_points)
