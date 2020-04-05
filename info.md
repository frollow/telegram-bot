Пример, как получить Id чата: 

def message_data(message): 
    chat_id = message.chat.id   
    return chat_id


Пример, получение данных о боте

print(bot.get_me())

Добавить новость

@bot.message_handler(commands=['add'])
def add_news(message):
    # or add KeyboardButton one row at a time:
    markup = types.ReplyKeyboardMarkup()
    vacancy = types.KeyboardButton('Предложить вакансию')
    resume = types.KeyboardButton('Ищу работу')
    markup.row(vacancy, resume)
    bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)