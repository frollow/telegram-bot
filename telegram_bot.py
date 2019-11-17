import telebot
import time
from telebot import types
from telebot import apihelper
import token_file
import requests

# proxy can be taken from https://hideip.me/ru/proxy/socks5list
apihelper.proxy = {'https': token_file.proxy_id}
bot = telebot.TeleBot(token_file.token_id)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     text='Привет, ' + message.from_user.first_name + '! Рады тебя видеть')
    bot.send_message(message.chat.id,
                     text='Жми на /lastnews и мы пришлем свежие объявления.')
    print(message)


@bot.message_handler(commands=['lastnews'])
def last_news(message):
    # or add KeyboardButton one row at a time:
    markup = types.ReplyKeyboardMarkup()
    vacancy = types.KeyboardButton('Ищу работу')
    resume = types.KeyboardButton('Ищу сотрудника')
    markup.row(vacancy, resume)
    bot.send_message(message.chat.id, "Что ты ищешь? Работу или сотрудника?", reply_markup=markup)
    print(message.text)


@bot.message_handler(content_types='text')
def send_news(message):
    if message.text == 'Ищу работу':
        bot.send_message(message.chat.id, "Сейчас пришлю список объявлений с вакансиями.")
        response = requests.get(token_file.url_vk + token_file.method_vk,
                                params=token_file.parameters_wall_vk)
        datas = response.json()['response']['items']
        posts = []
        posts.clear()
        resume = []
        resume.clear()
        yesterday = int(time.time()) - 86400
        for data in datas:
            if '#Работа_в_Рудном' in data['text'] and data['date'] > yesterday:
                print(208760)
                posts.append({
                    'date': data['date'],
                    'text': data['text'],
                    'author': data['owner_id']
                })
            elif '#Ищу_работу_в_Рудном' in data['text'] and data['date'] > yesterday:
                print(9898)
                resume.append({
                    'date': data['date'],
                    'text': data['text'],
                    'author': data['owner_id']
                })
            else:
                pass

        for post in posts:
            text = post['text']
            date = str(post['date'])
            author = str(post['author'])
            full_post = \
                f'''
{text}

Дата публикации: {date} 
Автор: {author}
                '''
            bot.send_message(message.chat.id, full_post)
    elif message.text == 'Ищу сотрудника':
        bot.send_message(message.chat.id, "Сейчас пришлю список объявлений о поиске работы.")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, 'Сорри, я не знаю как обработать это сообщение.')


# tested message to chat
bot.send_message(chat_id=178253335, text='Бот подключился')

# notification to console
print('Бот подключился')

# echo function, connected with telegram
bot.polling()
