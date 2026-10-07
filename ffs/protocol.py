import numpy as np
from pathlib import Path

from .layout import ROWS, COLS, Role
from .crypto import encrypt_payload, decrypt_payload


class Frame:
    # bits: encoded file bits - this is what gives each 8x8 pixel area a black/white color
    # roles: signifies the role of each 8x8 pixel area
    # frame_number: duh

    def __init__(self, frame_number):
        self.frame_number = frame_number
        self.bits = np.zeros((ROWS, COLS), dtype=np.uint8)
        self.roles = np.full((ROWS, COLS), Role.EMPTY,dtype=np.uint8)

        self._place_alignment_markers()
        self._reserve_metadata_area()
        self._assign_data_area()

    def set_cell(self, row, col, bit, role):
        self.bits[row, col] = bit
        self.roles[row, col] = role

    def _place_alignment_marker(self, top, left, size=7):
        # alignment marker placer :)
        # each marker is size x size logical cells
        
        for r in range(size):
            for c in range(size):
                rr = top + r
                cc = left + c

                # outer black border
                if r in (0, size - 1) or c in (0, size - 1):
                    self.set_cell(rr, cc, 1, Role.ALIGN)
                # inner white ring
                elif r in (1, size - 2) or c in (1, size - 2):
                    self.set_cell(rr, cc, 0, Role.ALIGN)
                # black center
                else:
                    self.set_cell(rr, cc, 1, Role.ALIGN)

    def _place_alignment_markers(self):
        # place all 4 

        size = 7
        
        self._place_alignment_marker(0, 0, size) # top left
        self._place_alignment_marker(0, COLS - size, size) # top right
        self._place_alignment_marker(ROWS - size, 0, size) # bottom left
        self._place_alignment_marker(ROWS - size, COLS - size, size) # bottom right

    def _reserve_metadata_area(self):
       # second row! TBC

        marker_size = 7
        self.roles[1, marker_size:COLS - marker_size] = Role.METADATA

    def _assign_data_area(self):
        # everything thats EMPTY is now reserved for data
        self.roles[self.roles == Role.EMPTY] = Role.DATA

    # per-frame data capacity
    def data_capacity_bits(self):
        return np.count_nonzero(self.roles == Role.DATA)

    def data_capacity_bytes(self):
        return self.data_capacity_bits() // 8

    def write_data(self, data):
        if len(data) > self.data_capacity_bytes():
            raise ValueError("data doesnt fit into frame")

        # convert bytes into bits
        data_bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))

        # get positions reserved for data
        data_positions = np.argwhere(self.roles == Role.DATA)

        for i, bit in enumerate(data_bits):
            row, col = data_positions[i]
            self.bits[row, col] = bit

        self._write_metadata(len(data))

    def _write_metadata(self, data_length):
        # frame number + number of actual data bytes in this frame
        metadata = self.frame_number.to_bytes(4, "big") + data_length.to_bytes(4, "big")
        metadata_bits = np.unpackbits(np.frombuffer(metadata, dtype=np.uint8))

        metadata_positions = np.argwhere(self.roles == Role.METADATA)

        for i, bit in enumerate(metadata_bits):
            row, col = metadata_positions[i]
            self.bits[row, col] = bit


# HELPERS!

def read_file(path):
    with open(path, "rb") as file:
        return file.read()


def make_file_payload(path, file_data):
    # filename only, without the original folders
    filename = Path(path).name.encode("utf-8")

    if len(filename) > 65535:
        raise ValueError("filename is too long")

    # format/version + filename length + original file size
    header = (
        b"FFS1"
        + len(filename).to_bytes(2, "big")
        + len(file_data).to_bytes(8, "big")
    )

    return header + filename + file_data


def read_file_payload(payload):
    if len(payload) < 14 or payload[:4] != b"FFS1":
        raise ValueError("missing or unsupported file header")

    filename_length = int.from_bytes(payload[4:6], "big")
    file_size = int.from_bytes(payload[6:14], "big")

    filename_end = 14 + filename_length

    if len(payload) < filename_end:
        raise ValueError("incomplete file header")

    filename = payload[14:filename_end].decode("utf-8")

    # only accept a filename, not a path
    if (
        not filename
        or filename in (".", "..")
        or "/" in filename
        or "\\" in filename
        or "\x00" in filename
        or Path(filename).is_absolute()
    ):
        raise ValueError("invalid filename")

    file_data = payload[filename_end:]

    if len(file_data) != file_size:
        raise ValueError("decoded file size does not match the header")

    return filename, file_data


def payload_to_file(payload, output_dir, recipient_private_key=None, encryption=True):
    if encryption:
        if recipient_private_key is None:
            raise ValueError("decryption requires a recipient private key")
        payload = decrypt_payload(payload, recipient_private_key)
    filename, file_data = read_file_payload(payload)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    # dont overwrite an existing file
    with open(output_path, "xb") as file:
        file.write(file_data)

    print("saved", output_path)


def file_to_frames(path, recipient_public_key=None, encryption=True):
    if encryption and recipient_public_key is None:
        raise ValueError("encryption requires a recipient public key")

    file_data = read_file(path)
    file_data = make_file_payload(path, file_data)
    if encryption:
        file_data = encrypt_payload(file_data, recipient_public_key)

    test_frame = Frame(0)
    capacity = test_frame.data_capacity_bytes()

    frames = []

    for i in range(0, len(file_data), capacity):
        chunk = file_data[i:i + capacity]

        frame = Frame(len(frames))
        frame.write_data(chunk)
        frames.append(frame)

    return frames


def read_metadata(bits, roles):
    metadata_positions = np.argwhere(roles == Role.METADATA)

    metadata_bits = []

    for row, col in metadata_positions:
        metadata_bits.append(bits[row, col])

    metadata_bits = np.array(metadata_bits[:64], dtype=np.uint8)
    metadata_bytes = np.packbits(metadata_bits).tobytes()

    frame_number = int.from_bytes(metadata_bytes[:4], "big")
    data_length = int.from_bytes(metadata_bytes[4:8], "big")

    return frame_number, data_length


def read_data(bits, roles, data_length):
    data_positions = np.argwhere(roles == Role.DATA)

    data_bits = []

    for row, col in data_positions[:data_length * 8]:
        data_bits.append(bits[row, col])

    data_bits = np.array(data_bits, dtype=np.uint8)

    return np.packbits(data_bits).tobytes()
