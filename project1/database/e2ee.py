from __future__ import annotations

import base64
from typing import Tuple, Union

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


AES_KEY_SIZE = 32  # AES-256


def aes_encrypt(text: str, key: bytes) -> Tuple[bytes, bytes]:
    if len(key) != AES_KEY_SIZE:
        raise ValueError("AES key must be 32 bytes for AES-256.")

    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(text.encode(), AES.block_size))
    return cipher.iv, ciphertext


def aes_decrypt(iv: bytes, ciphertext: bytes, key: bytes) -> str:
    if len(key) != AES_KEY_SIZE:
        raise ValueError("AES key must be 32 bytes for AES-256.")

    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode()


def generate_rsa_keys() -> Tuple[RSA.RsaKey, RSA.RsaKey]:
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
    if isinstance(message, str):
        message = message.encode()

    encryptor = PKCS1_OAEP.new(public_key)
    return encryptor.encrypt(message)


def rsa_decrypt(encrypted_message: bytes, private_key: RSA.RsaKey) -> bytes:
    decryptor = PKCS1_OAEP.new(private_key)
    return decryptor.decrypt(encrypted_message)


def hybrid_encrypt(message: str, public_key: RSA.RsaKey) -> Tuple[bytes, Tuple[bytes, bytes]]:
    aes_key = get_random_bytes(AES_KEY_SIZE)
    iv, ciphertext = aes_encrypt(message, aes_key)
    encrypted_aes_key = rsa_encrypt(aes_key, public_key)
    return encrypted_aes_key, (iv, ciphertext)


def hybrid_decrypt(
    encrypted_aes_key: bytes,
    encrypted_message: Tuple[bytes, bytes],
    private_key: RSA.RsaKey,
) -> str:
    aes_key = rsa_decrypt(encrypted_aes_key, private_key)
    iv, ciphertext = encrypted_message
    return aes_decrypt(iv, ciphertext, aes_key)


def to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def from_base64(data: str) -> bytes:
    return base64.b64decode(data.encode())
