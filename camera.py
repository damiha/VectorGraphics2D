import numpy as np
from pygame.examples.scroll import zoom_factor

from globals import *

class Camera:

    def __init__(self, camera_x=0.0, camera_y=0.0, zoom=1.0):
        self.camera_x = camera_x
        self.camera_y = camera_y
        self.zoom = zoom

    def move(self, mouse_dx, mouse_dy):

        # the further out you zoom, the faster the camera can move?
        self.camera_x += (mouse_dx * (1.0 / self.zoom))
        self.camera_y += (mouse_dy * (1.0 / self.zoom))

    def transform_change(self, dp):
        return (1.0 / self.zoom) * dp

    def change_zoom(self, d_zoom):

        if d_zoom < 0:
            self.zoom *= 0.9
        else:
            self.zoom *= 1.1

    def transform_point(self, p):

        # we want to zoom from the center of the current screen
        # first translate middle to (0,0)
        center_to_origin = np.array([-self.camera_x -WIDTH / 2, -self.camera_y -HEIGHT / 2])
        p = self.zoom * (p + center_to_origin) - center_to_origin

        return p + np.array([-self.camera_x, -self.camera_y])

    def inverse_transform_point(self, p):

        center_to_origin = np.array([-self.camera_x - WIDTH / 2, -self.camera_y - HEIGHT / 2])

        # inverse to 'transform point'
        p -= np.array([-self.camera_x, -self.camera_y])
        p += center_to_origin

        p /= self.zoom
        p -= center_to_origin

        return p
