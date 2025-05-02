import subprocess
import datetime
from os.path import join
from typing import Optional

from loguru import logger


# def backup_database(name_docker_container_postgres: str, user_name_postgres: str, name_db_postgres: str,
#                     description_db: str) -> Optional[str]:
#     """
#     Резервная копия базы данных
#     :param name_docker_container_postgres: имя вашего контейнера postgres
#     :param user_name_postgres: имя пользователя postgres
#     :param name_db_postgres: имя базы данных
#     :param description_db: от какого сервиса БД? будет использовать в имени файла
#     :return: Путь к файлу иначе None
#     """
#     try:
#         timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
#
#         backup_file = join('backups', f'{description_db}_backup_{timestamp}.sql')
#
#         command = ['docker', 'exec', name_docker_container_postgres, 'pg_dumpall', '-h', 'localhost', '-p', '5432',
#                    '-U', user_name_postgres]
#         with open(backup_file, 'wb') as file:
#             subprocess.run(command, stdout=file, check=True)
#     except Exception as e:
#         logger.error(str(e))
#         return
#
#     return backup_file


import datetime
import subprocess
from os.path import join
from typing import Optional

def backup_database(
    name_db_postgres: str,
    user_name_postgres: str,
    description_db: str,
    host: str = 'localhost',
    port: int = 5432,
    use_docker: bool = False,
    docker_container_name: Optional[str] = None
) -> Optional[str]:
    """
    Резервная копия базы данных PostgreSQL (локально или в контейнере Docker)

    :param name_db_postgres: имя базы данных
    :param user_name_postgres: имя пользователя postgres
    :param description_db: от какого сервиса БД? будет использоваться в имени файла
    :param host: адрес хоста PostgreSQL (по умолчанию 'localhost')
    :param port: порт PostgreSQL (по умолчанию 5432)
    :param use_docker: использовать ли Docker для выполнения резервного копирования
    :param docker_container_name: имя Docker-контейнера, если используется Docker
    :return: Путь к файлу, иначе None
    """
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_file = join('backups', f'{description_db}_backup_{timestamp}.sql')

        if use_docker:
            if not docker_container_name:
                raise ValueError("docker_container_name должен быть указан при use_docker=True")
            command = [
                'docker', 'exec', docker_container_name,
                'pg_dump', '-h', host, '-p', str(port),
                '-U', user_name_postgres, name_db_postgres
            ]
        else:
            command = [
                'pg_dump', '-h', host, '-p', str(port),
                '-U', user_name_postgres, name_db_postgres
            ]

        # with open(backup_file, 'wb') as file:
        #     subprocess.run(command, stdout=file, check=True, env={"PGPASSWORD": "your_password_here"})

        with open(backup_file, 'wb') as file:
                subprocess.run(command, stdout=file, check=True)

    except Exception as e:
        logger.error(f"Ошибка при создании бэкапа: {e}")
        return None

    return backup_file
