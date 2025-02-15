from os.path import abspath, join, dirname

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_keys(name_key: str = 'key', path_dir_save: str = None):
    """
    Генерация публичного и приватного ключа
    :param name_key: имя ключа. По-умочанию "key"
    :param path_dir_save: путь к директории куда требуется сохранить ключи, по-умолчнпю в директорию keys
    :return:
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    if path_dir_save is None:
        path_dir = dirname(abspath(__file__))
        path_dir_save = join(path_dir, 'keys')

    save_path_private_key = join(path_dir_save, f"private_{name_key}.pem")
    with open(save_path_private_key, "wb") as f:
        f.write(private_pem)

    save_path_public_key = join(path_dir_save, f"public_{name_key}.pem")
    with open(save_path_public_key, "wb") as f:
        f.write(public_pem)

    print(
        f"Приватный ключ: {save_path_private_key}\n"
        f"Публичный ключ: {save_path_public_key}"
    )

if __name__ == '__main__':
    generate_keys(name_key='new')
