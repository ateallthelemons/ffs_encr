from pathlib import Path

from ffs.video import video_to_file
from ffs.imaging import image_to_file
from ffs.crypto import load_private_key


# CONFIG
FILE_NAME = "encoded.mp4"  # use encoded.png for a single-frame image
ENCRYPTION = False  # match the setting used to encode the video


# EXECUTE!

project_dir = Path(__file__).resolve().parent
input_path = project_dir / "encoded" / FILE_NAME
output_dir = project_dir / "decoded"

recipient_private_key = None
if ENCRYPTION:
    recipient_private_key = load_private_key(project_dir / "keys/recipient_private.key")

if input_path.suffix.lower() == ".png":
    image_to_file(str(input_path), output_dir, recipient_private_key, encryption=ENCRYPTION)
else:
    video_to_file(str(input_path), output_dir, recipient_private_key, encryption=ENCRYPTION)
