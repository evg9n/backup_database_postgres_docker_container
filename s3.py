import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from os.path import split

from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from dateutil.tz import tzutc
from loguru import logger


class S3Client:
    """
    :param max_age_days: Максимальный возраст файлов в днях которые нужно будет удалить после заггрузки нового
    :param max_hours: Максимальный возраст файлов в часах которые нужно будет удалить после заггрузки нового
    :param max_minutes: Максимальный возраст файлов в минутах которые нужно будет удалить после заггрузки нового
    """
    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str,
            max_age_days: int = 0,
            max_hours: int = 0,
            max_minutes: int = 0
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()
        self.max_age_days = max_age_days
        self.max_hours = max_hours
        self.max_minutes = max_minutes

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(
            self,
            file_path: str,
            folder_name: str = './'
    ):
        if not folder_name.endswith('/'):
            folder_name += '/'
        object_name = f"{folder_name}{split(file_path)[1]}"
        try:
            async with self.get_client() as client:
                with open(file_path, "rb") as file:
                    await client.put_object(
                        Bucket=self.bucket_name,
                        Key=object_name,
                        Body=file,
                    )
                logger.info(f"Файл {object_name} загружен в {self.bucket_name}")
        except ClientError as e:
            logger.error(f"Ошибка загрузки файла: {e}")

        await self.delete_old_files(folder_name=folder_name)

    async def delete_file(self, object_name: str):
        try:
            async with self.get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
                logger.info(f"Файл {object_name} удален из {self.bucket_name}")
        except ClientError as e:
            logger.error(f"Ошибка удаления файла: {e}")

    async def get_file(self, object_name: str, destination_path: str):
        try:
            async with self.get_client() as client:
                response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
                data = await response["Body"].read()
                with open(destination_path, "wb") as file:
                    file.write(data)
                logger.info(f"Файл {object_name} загружен в {destination_path}")
        except ClientError as e:
            logger.error(f"Ошибка загрузка файла: {e}")

    async def delete_old_files(
            self, folder_name: str = './'
    ):
        """
        Удаляет все файлы в указанной директории (префиксе), которые старше указанного количества дней, часов, минут

        :param folder_name: Префикс (папка) для фильтрации файлов
        """
        if any([self.max_age_days > 0, self.max_hours > 0, self.max_minutes > 0]):
            try:
                async with self.get_client() as client:
                    # Вычисляем дату, старше которой файлы следует удалить
                    cutoff_date = datetime.now(tz=tzutc()) - timedelta(
                        days=self.max_age_days, hours=self.max_hours, minutes=self.max_minutes
                    )

                    # Получаем список всех объектов с указанным префиксом
                    paginator = client.get_paginator('list_objects_v2')

                    deleted_count = 0
                    # Итерируемся по страницам результатов
                    async for page in paginator.paginate(Bucket=self.bucket_name, Prefix=folder_name):
                        if "Contents" not in page:
                            continue

                        for obj in page["Contents"]:
                            # Проверяем дату последнего изменения
                            if obj["LastModified"].replace(tzinfo=tzutc()) < cutoff_date:
                                # Удаляем старый файл
                                object_key = obj["Key"]
                                await client.delete_object(Bucket=self.bucket_name, Key=object_key)
                                deleted_count += 1
                                logger.info(f"Удален старый файл: {object_key}, "
                                            f"дата редактирвания: {obj['LastModified']}")

                    logger.info(f"Удалено {deleted_count} файлов страже "
                                f"{self.max_age_days} дней "
                                f"{self.max_hours} часов "
                                f"{self.max_minutes} минут "
                                f"в {folder_name}")
                    return deleted_count

            except ClientError as e:
                logger.error(f"Ошибка при удалении старых файлов: {e}")
                return 0


async def main(path_file: str, access_key: str, secret_key: str, endpoint_url: str,
               bucket_name: str, folder_name: str = './',
               max_age_days: int = 0,
               max_hours: int = 0,
               max_minutes: int = 0):
    s3_client = S3Client(
        access_key=access_key,
        secret_key=secret_key,
        endpoint_url=endpoint_url,
        bucket_name=bucket_name,
        max_age_days=max_age_days,
        max_hours=max_hours,
        max_minutes=max_minutes
    )

    await s3_client.upload_file(path_file, folder_name)
