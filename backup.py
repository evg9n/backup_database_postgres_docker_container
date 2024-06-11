import subprocess
import datetime
from os.path import join

from loguru import logger


def backup_database(name_docker_container_postgres: str, user_name_postgres: str, name_db_postgres: str,
                    description_db: str):
    """
    Резервная копия базы данных
    :param name_docker_container_postgres: имя вашего контейнера postgres
    :param user_name_postgres: имя пользователя postgres
    :param name_db_postgres: имя базы данных
    :param description_db: от какого сервиса БД? будет использовать в имени файла
    :return: Путь к файлу иначе None
    """
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        backup_file = join('backups', f'{description_db}_backup_{timestamp}.sql')

        command = ['docker', 'exec', name_docker_container_postgres, 'pg_dump', '-U', user_name_postgres,
                   name_db_postgres]
        with open(backup_file, 'wb') as file:
            subprocess.run(command, stdout=file, check=True)
    except Exception as e:
        logger.error(str(e))
        return

    return backup_file
