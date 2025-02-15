from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from loguru import logger


def load_private_key(private_key_path):
    """
    Загрузка приватного ключа
    :param private_key_path: путь к приватному ключу
    :return: приватный ключ
    """
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )

    return private_key


def decrypt_file(encrypted_file_path, private_key):
    """
    Дешифровка файла
    :param encrypted_file_path: путь к зашифрованному файлу
    :param private_key: приватный ключ
    :return: дешифрованные данные
    """
    # Автоматическое определение максимального размера блока
    chunk_size = private_key.key_size // 8  # Максимальный размер блока данных(в байтах)
    decrypted_blocks = []

    with open(encrypted_file_path, "rb") as file:
        while True:
            encrypted_chunk = file.read(chunk_size)
            if not encrypted_chunk:
                break
            # Расшифровка блока
            decrypted_block = private_key.decrypt(
                encrypted_chunk,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            decrypted_blocks.append(decrypted_block)

    return b"".join(decrypted_blocks)


def save_decrypted_file(decrypted_data, output_path):
    """
    Сохранение дешифрованные данные
    :param decrypted_data: дешифрованные данные
    :param output_path: путь с именем куда сохранить дешифрованные данные
    :return:
    """
    with open(output_path, "wb") as file:
        file.write(decrypted_data)


def main(private_key_path: str, encrypted_file_path: str, decrypted_file_path: str) -> bool:
    """
    дешифрованние файла
    :param private_key_path: путь к приватному ключу
    :param encrypted_file_path: путь к зашифрованному файлу
    :param decrypted_file_path: путь с именем куда сохранить дешифрованные данные
    :return: True - успешно дешифрвоан файл, False - не удалось деширфовать
    """
    ok = False
    try:
        private_key = load_private_key(private_key_path)
        decrypted_data = decrypt_file(encrypted_file_path, private_key)
        save_decrypted_file(decrypted_data, decrypted_file_path)
        logger.info(f'Файл {encrypted_file_path} успешно дешифрован и сохранен в {decrypted_file_path}')
        ok = True

    except ValueError as error:
        if 'Decryption failed' in error.args:
            logger.error('Неверный приватный ключ')
        else:
            logger.error(error)

    except Exception as error:
        logger.error(error)

    finally:
        return ok
