# Files, Frames & Secrets


FFS is an experimental Python project that turns files into black-and-white grids in a PNG image or MP4 video. Send the image or video, then recover the original file—including its filename—on the receiving end. Encryption is optional.

| Input | Share | Restore |
| :--- | :--- | :--- |
| `data/your_file.ext` | `encoded/encoded.png` or `encoded/encoded.mp4` | `decoded/your_file.ext` |

## Getting started

The project has been tested with Python 3.13. From the project folder, create and activate a virtual environment:

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Then install the dependencies:

```bash
python -m pip install -r requirements.txt
```

On later visits, just activate the environment again. Each user creates their own `.venv/`; it is excluded from Git. Run all commands below from the project folder.

## Sharing a file

### 1. Choose your mode

Set `ENCRYPTION` in **both** `encode.py` and `decode.py`:

| Setting | Mode | Keys |
| :--- | :--- | :--- |
| `False` | Plain encoding | None needed |
| `True` | Encrypted transfer | Recipient's public/private key pair |

The settings must match; decoding does not auto-detect the mode.

For encrypted transfers, the **recipient** first runs `python generate_keys.py`. Give the sender `keys/recipient_public.key` to place in their own `keys/` folder. Keep `keys/recipient_private.key` private and retain it for decoding. Key generation is a one-time step and refuses to replace an existing `keys/` directory.

### 2. Send

Place your file in `data/` and set `FILENAME` in `encode.py` to its name, e.g. `"escapism.html"`.

For video output, the recommended starting settings in `encode.py` are:

| Setting | Default | Controls |
| :--- | :--- | :--- |
| `FPS` | `30` | Video frames per second |
| `DATA_FPS` | `10` | Distinct data frames per second |

At these values, each data frame is repeated **three times**. Increasing `DATA_FPS` produces a shorter video with fewer repetitions; decreasing it holds each data frame longer. Use positive integers with `DATA_FPS` no greater than `FPS`, and choose values where `FPS` is evenly divisible by `DATA_FPS`. These settings do not affect PNG output and do not guarantee recovery after platform compression.

```bash
python encode.py
```

If the payload fits in one frame, the encoder saves **`encoded/encoded.png`**; larger payloads become **`encoded/encoded.mp4`**. This includes the filename header and any encryption overhead. Share the file printed by the encoder. Each run replaces its selected output; an older output of the other type may remain.

### 3. Receive

Place the image or video in `encoded/`. Set `FILE_NAME` in `decode.py` to `"encoded.png"` or `"encoded.mp4"` as appropriate.

```bash
python decode.py
```

Your file appears in **`decoded/`** with its original name. Existing files are never overwritten; move or rename an earlier output before decoding it again.

## Under the hood

Encryption uses **HPKE: X25519 + HKDF-SHA256 + ChaCha20-Poly1305**, protecting both the contents and filename.

PNG output is lossless, but social platforms may resize or recompress uploads, so recovery after posting is not guaranteed. Decoding currently requires the original grid dimensions and alignment. Automatic alignment for cropped or phone-recorded video is not implemented. Damaged encrypted data fails verification; error correction is not yet implemented.
