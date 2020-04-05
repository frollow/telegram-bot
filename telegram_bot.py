import telebot
from telebot import apihelper
from telebot import types
import token_file
import requests
import csv
import time

# proxy can be taken from https://hideip.me/ru/proxy/socks5list
apihelper.proxy = {'https': token_file.proxy_id}
bot = telebot.TeleBot(token_file.token_id)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     text='Привет, ' + message.from_user.first_name + '! Рады тебя видеть')
    bot.send_message(message.chat.id,
                     text='Жми на /lastnews и мы пришлем свежие объявления.')
    try:
        result = user_in_the_list(message.json)
        if result == False:
            files_writer(message.json)
    except:
        pass


def user_in_the_list(users):
    user_id = users['from']['id']
    with open('parser_job.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(user_id) != int(row['telegram_id']):
                result = False
            else:
                result = True
                break
        file.close()
    if result == True:
        print('Пользователь уже есть в таблице')
    return result


# def update_stat(message):
#     user_id = message.json['from']['id']
#     with open('parser_job.csv', 'r', encoding='utf-8') as file:
#         reader = csv.DictReader(file)
#         writer = csv.DictWriter(file)
#         for row in reader:
#             if int(user_id) == int(row['telegram_id']):
#                 if message.text == 'Ищу работу':
#                     print('ищу работу')
#                     pass
#                 elif message.text == 'Ищу сотрудника':
#                     pass
#                 elif message.text == 'Предложить услугу':
#                     pass



def files_writer(users):
    with open('parser_job.csv', 'a', encoding='utf-8') as file:
        # w - all information will be rewrite in the file every time
        # a  - the new information will be added to the file
        a_pen = csv.writer(file)
        a_pen.writerow((users['from']['id'],
                        users['from']['username'],
                        users['from']['first_name'],
                        users['from']['last_name'],
                        0,
                        0,
                        0,
                        users['from']['is_bot'],
                        users['date'],
                        0))
        print('Пользователя добавили в таблицу')


@bot.message_handler(commands=['lastnews'])
def last_news(message):
    # or add KeyboardButton one row at a time:
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    vacancy = types.KeyboardButton('Ищу работу')
    resume = types.KeyboardButton('Ищу сотрудника')
    markup.add(vacancy, resume)
    bot.send_message(message.chat.id, "Ты в поиске работы или сотрудника?", reply_markup=markup)
    print("Пользователь сделал выбор")


@bot.message_handler(content_types='text')
def send_news(message):
    if message.text == 'Ищу работу':
        bot.send_message(message.chat.id, "Сейчас пришлю вакансии за "
                                          "последние 24 часа.")
        vk_group_posts('#Работа_в_Рудном', message)

    elif message.text == 'Ищу сотрудника':
        bot.send_message(message.chat.id, "Сейчас пришлю список объявлений о поиске работы за "
                                          "последние 24 часа.")
        vk_group_posts('#Ищу_работу_в_Рудном', message)
    else:
        bot.reply_to(message, 'Сорри, я еще не знаю как обработать это сообщение.')


def vk_data_take():
    response = requests.get(token_file.url_vk + token_file.method_vk,
                            params=token_file.parameters_wall_vk)
    datas = response.json()['response']['items']
    print('Данные пришли от VK')
    return datas


def vk_group_posts(hashtag, message):
    datas = vk_data_take()
    posts = []
    posts.clear()
    yesterday = int(time.time()) - 86400
    for data in datas:
        if hashtag in data['text'] and data['date'] > yesterday:
            print('Пост добавлен в список')
            posts.append({
                'date': data['date'],
                'text': data['text'],
                'author': data['signer_id']
            })
    for post in posts:
        text = post['text']
        date = time.strftime("%d.%m.%Y | %H:%M:%S", time.gmtime(post['date']))
        post_author = post["author"]
        author = f'https://m.vk.com/id{post_author}'
        full_post = \
            f'''
{text}

Дата: {date} 
Автор: {author}
            '''
        bot.send_message(message.chat.id, full_post)
    if len(posts) == 0:
        bot.send_message(message.chat.id,
                         "Опаньки... А объявлений пока нет. Попробуй чуть позже.")


# tested message to chat
bot.send_message(chat_id=178253335, text='Бот подключился')

# notification to console
print('Бот подключился')

# echo function, connected with telegram
while True:
    try:
        bot.polling(none_stop=True)
    # ConnectionError and ReadTimeout because of possible timout of the requests library
    # TypeError for moviepy errors
    # maybe there are others, therefore Exception
    except Exception as e:
        telebot.logger.error(e)
        time.sleep(15)
