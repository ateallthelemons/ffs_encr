from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.hpke import Suite, KEM, KDF, AEAD


# CONFIG
ENCRYPTION_HEADER = b"FFSE1"
ENCRYPTION_INFO = b"ffs_encr/" + ENCRYPTION_HEADER

SUITE = Suite(
    KEM.X25519,
    KDF.HKDF_SHA256,
    AEAD.CHACHA20_POLY1305,
)


def load_public_key(path):
    return X25519PublicKey.from_public_bytes(Path(path).read_bytes())


def load_private_key(path):
    return X25519PrivateKey.from_private_bytes(Path(path).read_bytes())


def encrypt_payload(payload, recipient_public_key):
    # HPKE creates a fresh ephemeral key for this file
    # its output includes the ephemeral public key and authentication tag
    encrypted = SUITE.encrypt(
        payload,
        recipient_public_key,
        info=ENCRYPTION_INFO,
    )

    return ENCRYPTION_HEADER + encrypted


def decrypt_payload(payload, recipient_private_key):
    if not payload.startswith(ENCRYPTION_HEADER):
        raise ValueError("missing or unsupported encryption header")

    encrypted = payload[len(ENCRYPTION_HEADER):]

    # at least the ephemeral public key + authentication tag
    if len(encrypted) < 32 + 16:
        raise ValueError("incomplete encrypted payload")

    try:
        return SUITE.decrypt(
            encrypted,
            recipient_private_key,
            info=ENCRYPTION_INFO,
        )
    except (InvalidTag, ValueError) as error:
        raise ValueError(
            "decryption failed: wrong key or damaged encrypted payload"
        ) from error
