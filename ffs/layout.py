import numpy as np
from enum import IntEnum

# CONFIG
WIDTH = 1920
HEIGHT = 1080
CELL = 8

ROWS = HEIGHT // CELL
COLS = WIDTH // CELL


class Role(IntEnum):
    EMPTY = 0
    DATA = 1
    ALIGN = 2
    METADATA = 4


def make_roles():
    roles = np.full((ROWS, COLS), Role.EMPTY,dtype=np.uint8)

    marker_size = 7

    # alignment markers
    roles[0:marker_size, 0:marker_size] = Role.ALIGN
    roles[0:marker_size, COLS - marker_size:COLS] = Role.ALIGN
    roles[ROWS - marker_size:ROWS, 0:marker_size] = Role.ALIGN
    roles[ROWS - marker_size:ROWS, COLS - marker_size:COLS] = Role.ALIGN

    # metadata
    roles[1,marker_size:COLS - marker_size] = Role.METADATA

    # everything else is data
    roles[roles == Role.EMPTY] = Role.DATA

    return roles
