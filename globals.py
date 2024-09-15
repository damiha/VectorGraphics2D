
from enum import Enum

# Set up colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WIDTH, HEIGHT = 800, 800

PASTEL_BLUE = (174, 198, 207)
PASTEL_RED = (255, 179, 186)

class Tool(Enum):
    TRANSLATE = 1
    DRAW = 2