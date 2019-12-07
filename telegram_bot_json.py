import telebot
from telebot import apihelper
from telebot import types
import token_file
import requests
import csv
import json
from pathlib import Path
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
        result = user_in_the_list(message)
        if result == False:
            add_user_to_file(message)
    except:
        pass


@bot.message_handler(commands=['statadmin'])
def stat_admin(message):
    user_id = message.json['from']['id']
    path = Path('users_list.json')
    data = json.loads(path.read_text(encoding='utf-8'))
    if user_id == 178253335:
        count_look_for_job = 0
        count_look_for_employer = 0
        for i in range(len(data)):
            if int(data[i]['telegram_id']) != 178253335:
                count_look_for_job = count_look_for_job + int(data[i]['look_for_job'])
                count_look_for_employer = count_look_for_employer + int(data[i]['look_for_employer'])
            else:
                print('Статистика отправлена. Данные админа не включены.')
        stat_post = \
            f'''
Популярность кнопок
Ищу работу: {count_look_for_job}
Ищу сотрудника: {count_look_for_employer} 
                    '''
        bot.send_message(message.chat.id, stat_post)
    else:
        pass


def user_in_the_list(message):
    user_id = message.json['from']['id']
    path = Path('users_list.json')
    data = json.loads(path.read_text(encoding='utf-8'))
    for i in range(len(data)):
        if user_id != int(data[i]['telegram_id']):
            result = False
        else:
            result = True
            break
    if result == True:
        print('Пользователь уже есть в таблице')
    return result


def add_user_to_file(message):
    user = {
        'telegram_id': int(message.json['from']['id']),
        'user_name': message.json['from']['username'],
        'first_name': message.json['from']['first_name'],
        'last_name': message.json['from']['last_name'],
        'look_for_job': 0,
        'look_for_employer': 0,
        'add_promo': 0,
        'is_bot': message.json['from']['is_bot'],
        'date_first_action': int(message.json['date']),
        'date_last_action': int(message.json['date']),
    }
    path = Path('users_list.json')
    data = json.loads(path.read_text(encoding='utf-8'))
    data.append(user)
    path.write_text(json.dumps(data,
                               ensure_ascii=False,
                               indent=4,
                               separators=(',', ': ')),
                    encoding='utf-8'
                    )

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
        try:
            update_stat(message)
        except:
            pass
    elif message.text == 'Ищу сотрудника':
        bot.send_message(message.chat.id, "Сейчас пришлю список объявлений о поиске работы за "
                                          "последние 24 часа.")
        vk_group_posts('#Ищу_работу_в_Рудном', message)
        try:
            update_stat(message)
        except:
            pass
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


def update_stat(message):
    user_id = message.json['from']['id']
    path = Path('users_list.json')
    data = json.loads(path.read_text(encoding='utf-8'))
    for i in range(len(data)):
        if user_id == int(data[i]['telegram_id']):
            if message.text == 'Ищу работу':
                data[i]['look_for_job'] = data[i]['look_for_job'] + 1
                data[i]['date_last_action'] = int(message.json['date'])
                if data[i]['user_name'] == 'no':
                    data[i]['user_name'] = message.json['from']['username']
                path.write_text(json.dumps(data,
                                           ensure_ascii=False,
                                           indent=4,
                                           separators=(',', ': ')),
                                encoding='utf-8'
                                )
            elif message.text == 'Ищу сотрудника':
                data[i]['look_for_employer'] = data[i]['look_for_employer'] + 1
                data[i]['date_last_action'] = int(message.json['date'])
                if data[i]['user_name'] == 'no':
                    data[i]['user_name'] = message.json['from']['username']
                path.write_text(json.dumps(data,
                                           ensure_ascii=False,
                                           indent=4,
                                           separators=(',', ': ')),
                                encoding='utf-8'
                                )
            elif message.text == 'Предложить услугу':
                pass


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
