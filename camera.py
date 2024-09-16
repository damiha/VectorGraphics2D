
class Camera:

    def __init__(self, camera_x=0.0, camera_y=0.0, zoom=1.0):
        self.camera_x = camera_x
        self.camera_y = camera_y
        self.zoom = zoom

    def move(self, dx, dy):
        self.camera_x += dx
        self.camera_y += dy

    def zoom(self, new_zoom_val):
        raise NotImplementedError
