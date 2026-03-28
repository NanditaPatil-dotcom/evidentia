from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("ENCRYPTION_KEY")
fernet = Fernet(key)


def encrypt_file(path):
    with open(path, "rb") as f:
        data = f.read()

    encrypted = fernet.encrypt(data)

    enc_path = path + ".enc"

    with open(enc_path, "wb") as f:
        f.write(encrypted)

    return enc_path


def decrypt_file(enc_path, output_path):
    with open(enc_path, "rb") as f:
        data = f.read()

    decrypted = fernet.decrypt(data)

    with open(output_path, "wb") as f:
        f.write(decrypted)

    return output_path