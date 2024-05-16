import telebot
import math
from gpt import ask_gpt, tts, stt, count_all_tokens, PROMT, create_new_token
from sql import *
import logging

logging.basicConfig(filename='logs.txt', level=logging.INFO,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

# Токен бота
bot = telebot.TeleBot(token='')

max_tokens = 10000
max_blocks = 50
max_symbols = 15000
max_sessions = 20000


@bot.message_handler(commands=['start'])
def start(message):
    create_users_table()
    create_users_content_table()
    if not get_data_for_user(message.from_user.id):
        data = get_data('users')
        if len(list(data)) >= 2:
            bot.send_message(message.from_user.id, f"""
                Здравствуйте, к сожалению мы не можем допустить Вас к пользованию ботом так достигнуто максимальное количество пользователей.""")
            return
        else:
            insert_row_users((message.from_user.id, 0, 0, 0, 0))

    bot.send_message(message.from_user.id, f"""
    Добро пожаловать в бота - голосового помошника, {message.from_user.first_name}, он ответит на любой Ваш вопрос! Можете отправить вопрос как в текстовом формате так и голосовым сообщением, бот Вас поймет!""")


@bot.message_handler(commands=['stt'])
def test_stt1(message):
    bot.send_message(message.from_user.id, 'Отправьте голосовое сообщение длиной до 15 секунд чтобы проверить распознование речи.')
    bot.register_next_step_handler(message, test_stt2)


def test_stt2(message):
    if message.voice.duration > 15 or message.content_type != 'voice':
        bot.send_message(message.from_user.id,'Отправьте другое голосовое сообщение.')
        bot.register_next_step_handler(message, test_stt2)
    try:
        file_id = message.voice.file_id  # получаем id голосового сообщения
        file_info = bot.get_file(file_id)  # получаем информацию о голосовом сообщении
        file = bot.download_file(file_info.file_path)

        bot.send_message(message.from_user.id,
                     f'Если вы сказали "{stt(file)}", то все работает корректно')
    except:
        bot.send_message(message.from_user.id,'Возможно вы ничего не говорили во время записи сообщения. Повторите попытку')
        bot.register_next_step_handler(message, test_stt2)


@bot.message_handler(commands=['tts'])
def test_tts(message):
    bot.send_message(message.from_user.id,
                     'Вам должно будет прийти голосовое сообщение.')
    bot.send_voice(message.from_user.id, tts('Если вы это слышите то все работает корректно.'))


@bot.message_handler(content_types=['text'])
def ask_text(message):
    create_new_token()
    data = get_data_for_user(message.from_user.id)

    if data[0][3] > 10000:
        bot.send_message(message.from_user.id, f"""
            Вы израсходовали максимально колличество токенов.""")
    elif data[0][2] > 15:
        bot.send_message(message.from_user.id, f"""
        Вы израсходовали максимально колличество cессийч.""")

    gpt_answer = ask_gpt(message.text)
    messages = [{"role": "system", "text": PROMT}, {"role": "user", "text": message.text},
                    {"role": "assistant", "text": gpt_answer}]
    tokens = count_all_tokens(messages)

    update_row_value(message.from_user.id, 'tokens_used', data[0][3] + tokens)
    update_row_value(message.from_user.id, 'sessions', data[0][2] + 1)

    insert_row_users_content((message.from_user.id, "user", message.text))
    insert_row_users_content((message.from_user.id, "assistant", gpt_answer))

    bot.send_message(message.from_user.id, f"""
    ответ GPT: {gpt_answer}""")


@bot.message_handler(content_types=['voice'])
def ask_voice(message):
    create_new_token()
    data = get_data_for_user(message.from_user.id)

    if data[0][3] > 10000:
        bot.send_message(message.from_user.id, f"""Вы израсходовали максимально колличество токенов.""")
    elif data[0][2] > 15:
        bot.send_message(message.from_user.id, f"""Вы израсходовали максимально колличество cессий.""")
    elif data[0][4] + math.ceil(message.voice.duration / 15) > 50:
        bot.send_message(message.from_user.id, f"""Вы израсходовали максимально колличество аудио блоков.""")
    elif data[0][5] > 20000:
        bot.send_message(message.from_user.id, f"""Вы израсходовали максимально колличество символов для озвучки.""")

    file_id = message.voice.file_id  # получаем id голосового сообщения
    file_info = bot.get_file(file_id)  # получаем информацию о голосовом сообщении
    file = bot.download_file(file_info.file_path)

    file1 = stt(file)
    update_row_value(message.from_user.id, 'blocks_used', data[0][4] + math.ceil(message.voice.duration / 15))

    file2 = ask_gpt(file1)
    messages = [{"role": "system", "text": PROMT}, {"role": "user", "text": file1},
                    {"role": "assistant", "text": file2}]
    tokens = count_all_tokens(messages)
    update_row_value(message.from_user.id, 'tokens_used', data[0][3] + tokens)

    bot.send_voice(message.from_user.id, tts(file2))
    update_row_value(message.from_user.id, 'symbols_used', data[0][5] + len(file2))

    insert_row_users_content((message.from_user.id, "user", file1))
    insert_row_users_content((message.from_user.id, "assistant", file2))


bot.polling()