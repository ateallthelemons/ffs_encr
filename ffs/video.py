import cv2

from .layout import WIDTH, HEIGHT, make_roles
from .imaging import frame_to_array, image_to_bits
from .protocol import read_metadata, read_data, payload_to_file


def frames_to_video(frames, path, fps=30, data_fps=30):
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    video = cv2.VideoWriter(path, fourcc, fps, (WIDTH, HEIGHT))

    repeats = fps // data_fps

    for frame in frames:
        image = frame_to_array(frame)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        for _ in range(repeats):
            video.write(image)

    video.release()


def video_to_file(video_path, output_dir, recipient_private_key=None, encryption=True):
    if encryption and recipient_private_key is None:
        raise ValueError("decryption requires a recipient private key")

    roles = make_roles()
    video = cv2.VideoCapture(video_path)

    decoded_frames = {}

    while True:
        success, image = video.read()

        if not success:
            break

        bits = image_to_bits(image)

        frame_number, data_length = read_metadata(bits, roles)

        # repeated video frames will contain the same logical frame
        if frame_number in decoded_frames:
            continue

        data = read_data(bits, roles, data_length)
        decoded_frames[frame_number] = data

        print("decoded frame", frame_number, "-", data_length, "bytes")

    video.release()

    # put the complete payload back together before reading its header
    payload = b"".join(
        decoded_frames[frame_number]
        for frame_number in sorted(decoded_frames)
    )

    payload_to_file(payload, output_dir, recipient_private_key, encryption=encryption)
