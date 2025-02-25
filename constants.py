from os import environ, path, listdir, getenv

from dotenv import load_dotenv


class Constants:

    def __init__(self):
        load_dotenv(path.abspath(path.join('env', '.env')))
        path_env = path.abspath('env')
        try:
            for env in listdir(path_env):
                if env.endswith('.env'):
                    load_dotenv(path.join(path_env, env))
        except FileNotFoundError:
            pass

        # логирование
        self.FORMAT_LOGGER = getenv('FORMAT_LOGGER',
                                    default='{time:YYYY-MM-DD HH:mm:ss} | {level} | {file} | {message}')
        self.LEVEL_FILE_LOGGER = getenv('LEVEL_FILE_LOGGER', default='DEBUG')
        self.LEVEL_CONSOLE_LOGGER = getenv('LEVEL_CONSOLE_LOGGER', default='INFO')
        self.ROTATION_LOGGER = getenv('ROTATION_LOGGER', default='1 day')
        self.SERIALIZE_LOGGER = getenv('SERIALIZE_LOGGER', default=None) == 'True'

        self.SEND_BOT_BACKUP = environ.get('SEND_BOT_BACKUP') == 'true'
        self.SEND_S3_BACKUP = environ.get('SEND_S3_BACKUP') == 'true'
        self.SAVE_BACKUP = environ.get('SAVE_BACKUP') == 'true'
        self.USE_ENCRYPTO = environ.get('USE_ENCRYPTO') == 'true'

        if self.SEND_BOT_BACKUP:
            # telegram bot
            self.BOT_TOKEN = environ.get('BOT_TOKEN')
            assert self.BOT_TOKEN, 'Не найден BOT_TOKEN в env-файле'
            bot_list_users_id = environ.get('BOT_LIST_USERS_ID')
            assert bot_list_users_id, 'Не найден BOT_LIST_USERS_ID в env-файле'
            self.BOT_LIST_USERS_ID = bot_list_users_id.split(',')

        if self.SEND_S3_BACKUP:
            # S3
            self.S3_ACCESS_KEY = environ.get('S3_ACCESS_KEY')
            assert self.S3_ACCESS_KEY, 'Не найден S3_ACCESS_KEY в env-файле'

            self.S3_SECRET_KEY = environ.get('S3_SECRET_KEY')
            assert self.S3_SECRET_KEY, 'Не найден S3_SECRET_KEY в env-файле'

            self.S3_ENDPOINT_URL = environ.get('S3_ENDPOINT_URL')
            assert self.S3_ENDPOINT_URL, 'Не найден S3_ENDPOINT_URL в env-файле'

            self.S3_BUCKET_NAME = environ.get('S3_BUCKET_NAME')
            assert self.S3_BUCKET_NAME, 'Не найден S3_BUCKET_NAME в env-файле'

            self.S3_PATH_FOLDER = environ.get('S3_PATH_FOLDER', '.')

        # postgres
        self.NAME_DOCKER_CONTAINER_POSTGRES = environ.get('NAME_DOCKER_CONTAINER_POSTGRES')
        assert self.NAME_DOCKER_CONTAINER_POSTGRES, 'Не найден NAME_DOCKER_CONTAINER_POSTGRES в env-файле'

        self.USER_NAME_POSTGRES = environ.get('USER_NAME_POSTGRES')
        assert self.USER_NAME_POSTGRES, 'Не найден USER_NAME_POSTGRES в env-файле'

        self.NAME_DB_POSTGRES = environ.get('NAME_DB_POSTGRES')
        assert self.NAME_DB_POSTGRES, 'Не найден NAME_DB_POSTGRES в env-файле'

        self.DESCRIPTION_DB = environ.get('DESCRIPTION_DB')
        assert self.DESCRIPTION_DB, 'Не найден DESCRIPTION_DB в env-файле'

        # encrypt
        if self.USE_ENCRYPTO:
            self.PATH_PUBLIC_KEY_ENCRYPTO = environ.get('PATH_PUBLIC_KEY_ENCRYPTO')
            assert self.PATH_PUBLIC_KEY_ENCRYPTO, 'Не найден DESCRIPTION_DB в env-файле'

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise AttributeError('Constants are not changeable!')
        else:
            super().__setattr__(name, value)
