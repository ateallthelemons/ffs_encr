import os
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey


def generate_keys(output_dir):
    private_key = X25519PrivateKey.generate()
    public_key = private_key.public_key()

    output_dir = Path(output_dir)

    # dont replace an existing key pair
    output_dir.mkdir(mode=0o700)

    private_path = output_dir / "recipient_private.key"
    public_path = output_dir / "recipient_public.key"

    # only the current user can read/write the private key
    descriptor = os.open(
        private_path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600,
    )

    with os.fdopen(descriptor, "wb") as file:
        file.write(private_key.private_bytes_raw())

    with open(public_path, "xb") as file:
        file.write(public_key.public_bytes_raw())

    print("private key:", private_path)
    print("public key:", public_path)


# EXECUTE!

if __name__ == "__main__":
    generate_keys("keys")
