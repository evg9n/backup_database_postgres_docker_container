from os import remove
from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from loguru import logger


def load_public_key(public_key_path):
    """
    Загрузка публичного ключа
    :param public_key_path: путь к публичному ключу
    :return: публичный ключ
    """
    with open(public_key_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read()
        )
    return public_key


def encrypt_file(file_to_encrypt, public_key):
    """
    Шифрование файла с использованием RSA.
    :param file_to_encrypt: путь к файлу, который требуется зашифровать
    :param public_key: публичный ключ
    :return: список зашифрованных блоков
    """
    # Автоматическое определение максимального размера блока
    key_size_bytes = public_key.key_size // 8  # Размер ключа в байтах
    padding_overhead = 2 * hashes.SHA256().digest_size + 2  # Размер служебных данных для OAEP
    chunk_size = key_size_bytes - padding_overhead  # Максимальный размер блока данных
    encrypted_blocks = []

    with open(file_to_encrypt, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            # Шифрование блока
            encrypted_block = public_key.encrypt(
                chunk,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            encrypted_blocks.append(encrypted_block)

    return encrypted_blocks



def save_encrypted_file(encrypted_data, output_path):
    """
    Сохранение зашифрованного файла
    :param encrypted_data: данные зашифрованого файла
    :param output_path: путь куда будет сохранен зашифрованный файл
    :return:
    """
    with open(output_path, "wb") as file:
        for block in encrypted_data:
            file.write(block)


def main(public_key_path: str, file_to_encrypt: str, encrypted_file_path: str = None,
         delete_origin_file: bool = False) -> Optional[str]:
    """
    Шифрование файла
    :param public_key_path: Публичный ключ
    :param file_to_encrypt: Путь к файлу который требуется зашифровать
    :param encrypted_file_path: Путь с именем куда будет сохранен зашифрованный файл,
    по-умоланию будет использован file_to_encrypt
    :param delete_origin_file: True - после успешной зашифровки будет удален оригинальный файл, по-умолчанию False
    :return: путь к зашифрованному файлу, None если не получтлось зашифровать
    """
    path_encrypt = None

    if encrypted_file_path is None:
        encrypted_file_path = file_to_encrypt + '.enc'

    try:
        public_key = load_public_key(public_key_path)
        encrypted_data = encrypt_file(file_to_encrypt, public_key)
        save_encrypted_file(encrypted_data, encrypted_file_path)
        logger.info(f'Файл {file_to_encrypt} успешно зашифрован и сохранен в {encrypted_file_path}')
        path_encrypt = encrypted_file_path
        if delete_origin_file:
            remove(file_to_encrypt)
    except Exception as error:
        logger.error(error.args)
    finally:
        return path_encrypt
