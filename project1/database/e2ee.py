from __future__ import annotations

import base64
from typing import Tuple, Union

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


AES_KEY_SIZE = 32  # AES-256


def aes_encrypt(text: str, key: bytes) -> Tuple[bytes, bytes]:
    """Encrypt plaintext using AES-256-CBC and return (iv, ciphertext)."""
    if len(key) != AES_KEY_SIZE:
        raise ValueError("AES key must be 32 bytes for AES-256.")

    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(text.encode(), AES.block_size))
    return cipher.iv, ciphertext


def aes_decrypt(iv: bytes, ciphertext: bytes, key: bytes) -> str:
    """Decrypt AES-256-CBC ciphertext with the matching IV/key."""
    if len(key) != AES_KEY_SIZE:
        raise ValueError("AES key must be 32 bytes for AES-256.")

    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode()


def generate_rsa_keys() -> Tuple[RSA.RsaKey, RSA.RsaKey]:
    """Generate a 2048-bit RSA keypair and return (private_key, public_key)."""
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    return private_key, public_key


def get_public_key_pem(public_key: RSA.RsaKey) -> str:
    return public_key.export_key().decode()


def get_private_key_pem(private_key: RSA.RsaKey) -> str:
    return private_key.export_key().decode()


def load_public_key_pem(pem_data: Union[str, bytes]) -> RSA.RsaKey:
    if isinstance(pem_data, str):
        pem_data = pem_data.encode()
    return RSA.import_key(pem_data)


def load_private_key_pem(pem_data: Union[str, bytes]) -> RSA.RsaKey:
    if isinstance(pem_data, str):
        pem_data = pem_data.encode()
    return RSA.import_key(pem_data)


def rsa_encrypt(message: Union[str, bytes], public_key: RSA.RsaKey) -> bytes:
    """Encrypt bytes/string with RSA-OAEP public key encryption."""
    if isinstance(message, str):
        message = message.encode()

    max_message_length = public_key.size_in_bytes() - (2 * SHA256.digest_size) - 2
    if len(message) > max_message_length:
        raise ValueError(
            f"Message too long for RSA OAEP encryption. Max length is {max_message_length} bytes."
        )

    encryptor = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
    return encryptor.encrypt(message)


def rsa_decrypt(encrypted_message: bytes, private_key: RSA.RsaKey) -> bytes:
    """Decrypt RSA-OAEP ciphertext using the RSA private key."""
    decryptor = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
    return decryptor.decrypt(encrypted_message)


def hybrid_encrypt(message: str, public_key: RSA.RsaKey) -> Tuple[bytes, Tuple[bytes, bytes]]:
    """Return (encrypted_aes_key, (iv, ciphertext)) for the given plaintext."""
    aes_key = get_random_bytes(AES_KEY_SIZE)
    iv, ciphertext = aes_encrypt(message, aes_key)
    encrypted_aes_key = rsa_encrypt(aes_key, public_key)
    return encrypted_aes_key, (iv, ciphertext)


def hybrid_decrypt(
    encrypted_aes_key: bytes,
    encrypted_message: Tuple[bytes, bytes],
    private_key: RSA.RsaKey,
) -> str:
    """Decrypt (encrypted_aes_key, (iv, ciphertext)) back to plaintext."""
    aes_key = rsa_decrypt(encrypted_aes_key, private_key)
    iv, ciphertext = encrypted_message
    return aes_decrypt(iv, ciphertext, aes_key)


def to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def from_base64(data: str) -> bytes:
    return base64.b64decode(data.encode())
