from pathlib import Path

from ffs.protocol import file_to_frames
from ffs.video import frames_to_video
from ffs.imaging import frame_to_image
from ffs.crypto import load_public_key


# CONFIG
FILENAME = "to_encode.ext"
ENCRYPTION = True  # False for plain bit encoding
FPS = 30      # video framerate - adjust to comply with platform requirements
DATA_FPS = 30 # data framerate - higher values allow more data/sec but
              # may cause more noise during compression - i.e. the data may 
              # become unrecoverable due to platform dictated compression.


# EXECUTE!

project_dir = Path(__file__).resolve().parent
filename = Path(FILENAME).name
input_path = project_dir / "data" / filename
output_dir = project_dir / "encoded"
output_dir.mkdir(exist_ok=True)

recipient_public_key = None
if ENCRYPTION:
    recipient_public_key = load_public_key(project_dir / "keys/recipient_public.key")

frames = file_to_frames(input_path, recipient_public_key, encryption=ENCRYPTION)

print(len(frames))
if len(frames) == 1:
    output_path = output_dir / "encoded.png"
    frame_to_image(frames[0], output_path)
else:
    output_path = output_dir / "encoded.mp4"
    frames_to_video(frames, str(output_path), fps=FPS, data_fps=DATA_FPS)

print("saved", output_path)
