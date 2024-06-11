from telebot import TeleBot
from loguru import logger


def send_file_via_telegram(file_path: str, bot_token: str, bot_list_users_id: list, description_db: str = None) -> bool:
    """
    Отправка файла через телеграм-бота
    :param file_path: Путь к файлу
    :param bot_token: токен бота
    :param bot_list_users_id: list user_id пользователей кому отправить
    :param description_db: от какого сервиса БД? будет использовать в имени файла
    :return: bool, False - неуспешно, True - успешно
    """
    try:
        bot = TeleBot(token=bot_token)
        if file_path:
            with open(file_path, 'rb') as file:
                for user_id in bot_list_users_id:
                    bot.send_document(chat_id=user_id, document=file)
        else:
            for user_id in bot_list_users_id:
                    bot.send_message(chat_id=user_id, text=f'Не получилось сделать резервную копию {description_db}')
    except Exception as e:
        logger.error(str(e))
        return False

    return True
