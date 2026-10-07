import numpy as np
import cv2
from PIL import Image

from .layout import WIDTH, HEIGHT, CELL, ROWS, COLS, Role, make_roles
from .protocol import read_metadata, read_data, payload_to_file


def frame_to_array(frame):
    image = np.kron(frame.bits, np.ones((CELL, CELL), dtype=np.uint8)) * 255

    padded = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
    padded[:image.shape[0], :image.shape[1]] = image

    return padded


def frame_to_image(frame, path):
    image = frame_to_array(frame)
    Image.fromarray(image).save(path)


def image_to_file(image_path, output_dir, recipient_private_key=None, encryption=True):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("could not read image")
    if image.shape[:2] != (HEIGHT, WIDTH):
        raise ValueError("image dimensions do not match the grid")

    roles = make_roles()
    bits = image_to_bits(image)
    frame_number, data_length = read_metadata(bits, roles)

    if frame_number != 0 or not 0 < data_length <= np.count_nonzero(roles == Role.DATA) // 8:
        raise ValueError("invalid single-frame image metadata")

    payload = read_data(bits, roles, data_length)
    payload_to_file(payload, output_dir, recipient_private_key, encryption=encryption)


def image_to_bits(image):
    # use grayscale
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    bits = np.zeros((ROWS, COLS), dtype=np.uint8)

    for row in range(ROWS):
        for col in range(COLS):
            y1 = row * CELL
            y2 = y1 + CELL
            x1 = col * CELL
            x2 = x1 + CELL

            block = image[y1:y2, x1:x2]

            # average brightness of the whole cell
            bits[row, col] = 1 if np.mean(block) > 127 else 0

    return bits
