
from enum import Enum

# Set up colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WIDTH, HEIGHT = 800, 800

PASTEL_BLUE = (174, 198, 207)
PASTEL_RED = (255, 179, 186)
PASTEL_GREEN = (193, 225, 193)
BRIGHT_ORANGE = (255, 140, 0)

GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

HANDLE_RADIUS = 10

class Tool(Enum):
    TRANSLATE = 1
    DRAW = 2
    CLOSE = 3
    FILL = 4
    LINK = 5