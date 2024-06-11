# Логгер
import asyncio

from loguru import logger

from os.path import abspath, join
from os import remove

from backup import backup_database
from send import send_file_via_telegram
from s3 import main

# Константы
from constants import Constants


c = Constants()

logger.remove()
logger.add(
    abspath(join('logs', '{time:YYYY-MM-DD  HH.mm.ss}.log')),  # Путь к файлу логов с динамическим именем
    rotation=c.ROTATION_LOGGER,  # Ротация логов каждый день
    compression="zip",  # Использование zip-архива
    level=c.LEVEL_FILE_LOGGER,  # Уровень логирования
    format=c.FORMAT_LOGGER,  # Формат вывода
    serialize=c.SERIALIZE_LOGGER,  # Сериализация в JSON
)

# Вывод лога в консоль
logger.add(
    sink=print,
    level=c.LEVEL_CONSOLE_LOGGER,
    format=c.FORMAT_LOGGER,
)


if __name__ == '__main__':
    logger.info('RUN PROJECT')
    backup_file = backup_database(c.NAME_DOCKER_CONTAINER_POSTGRES, c.USER_NAME_POSTGRES, c.NAME_DB_POSTGRES,
                                  c.DESCRIPTION_DB)
    logger.info(f'{backup_file=}')

    if backup_file:
        result_send = None
        if c.SEND_BOT_BACKUP:
            # Отправляем файл через Telegram бота
            result_send = send_file_via_telegram(backup_file, c.BOT_TOKEN, c.BOT_LIST_USERS_ID)
            logger.info(f'{result_send=}')
            # if not c.SAVE_BACKUP and result_send:
            #     # Удаляем файл
            #     remove(backup_file)

        if c.SEND_S3_BACKUP:
            asyncio.run(main(
                path_file=backup_file,
                access_key=c.S3_ACCESS_KEY,
                secret_key=c.S3_SECRET_KEY,
                endpoint_url=c.S3_ENDPOINT_URL,
                bucket_name=c.S3_BUCKET_NAME,
            ))

        if result_send and any([c.SEND_BOT_BACKUP]):
            if not c.SAVE_BACKUP:
                # Удаляем файл
                remove(backup_file)

    elif c.SEND_BOT_BACKUP:
        send_file_via_telegram(backup_file, c.BOT_TOKEN, c.BOT_LIST_USERS_ID, c.DESCRIPTION_DB)
