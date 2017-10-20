import urllib.request as urllib
import telebot
import random
import pyowm
import requests
import urllib.request
from bs4 import BeautifulSoup

# from telebot import types

greetings = ["Привет", "Буэнос айрос, диаз", "Здравствуй", "Салют!", "Я тут", "Привет-привет",
             "Здравствуй, мама – Здравствуй, сынок "]
how_are_you = ["Отлично", "Хорошо", "Супер!", "Норм", "Сойдёт", "Гуд", "В порядке"]

token = "438690794:AAHFnB_R5blFZtUppviH0htRDtvC8oeMxuo"
bot = telebot.TeleBot(token)
KEYYANDEXTR = 'trnsl.1.1.20170307T125725Z.f5d3d87760f627de.7860f7f5c43409ed29297d5eb8fa810e2028b7d1'


# bot.send_message(274804508, "Я")
# bot.send_message(187405139, "Дима")
# bot.send_message(218237598, "Роанд, ...")
#

@bot.message_handler(commands=['start'])
def start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Переводчик \u2618', 'Погода \u2601')
    user_markup.row('Фото дня', 'Новости')
    user_markup.row('Загрузить Kate Mobile')
    bot.send_message(message.chat.id, "Привет, " + message.chat.first_name +
                     "! Я тебя люблю" + "\U0001F618", reply_markup=user_markup)


@bot.message_handler(content_types=['text'])
def home(message):
    if message.text == "Привет" or message.text == "привет":
        bot.send_message(message.chat.id, random.choice(greetings))
    elif message.text == "Как дела?":
        bot.send_message(message.chat.id, random.choice(how_are_you))
    elif message.text == "Фото дня":
        url = 'https://yandex.ru/images/today?size='
        urllib.request.urlretrieve(url, 'url_image.jpg')
        img = open('url_image.jpg', 'rb')
        bot.send_chat_action(message.from_user.id, 'upload_photo')
        bot.send_photo(message.from_user.id, img)
        img.close()

    elif message.text == "Загрузить Kate Mobile":
        bot.send_message(message.chat.id, "*Загрузить Kate Mobile сейчас невозможно.* Сожалеем об этом.", parse_mode="Markdown")
#        url = "http://katemobile.ru/dl/Kate.apk"
#        urllib.urlretrieve(url, 'Kate.apk')
#        document = open('kate.apk', 'rb')
#        bot.send_chat_action(message.from_user.id, 'upload_document')
#        bot.send_document(message.from_user.id, document)
#        document.close()

    elif message.text == "Погода \u2601" or message.text == "Погода":
        bot.send_message(message.chat.id, "В каком городе показать погоду?")
        bot.register_next_step_handler(message, weath)
    elif message.text == "Переводчик \u2618" or message.text == "Переводчик":
        translate_text = bot.send_message(message.chat.id, "Что перевести?" " RUS - ENG")
        bot.register_next_step_handler(translate_text, get_translate_text)
    elif message.text == "Новости":
        r = requests.get("http://yandex.ru")
        soup = BeautifulSoup(r.text, "html.parser")
        news = soup.find_all(class_="home-link list__item-content home-link_black_yes")
        bot.send_message(message.chat.id, "*Главные новости:*", parse_mode="Markdown")
        for new_cur in news[0:3]:
            bot.send_message(message.chat.id, new_cur.get("aria-label"))
        bot.send_message(message.chat.id, "*Санкт-Петербург:*", parse_mode="Markdown")
        for new_cur in news[5:10]:
            bot.send_message(message.chat.id, new_cur.get("aria-label"))

def GetTodayImageName():
    url = "https://yandex.ru/images/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    today_image_name = soup.find('span', {'class': 'b-501px__name'}).text
    return today_image_name


def weath(message):
    owm = pyowm.OWM("7a6fea5b5a154258520d82a4a882dfeb", language="ru")
    city = message.text
    weather = owm.weather_at_place(city)
    w = weather.get_weather()
    temperature = w.get_temperature("celsius")["temp"]
    wind = w.get_wind()["speed"]
    hum = w.get_humidity()
    desc = w.get_detailed_status()
    bot.send_message(message.chat.id, "Сейчас в городе " + str(city) + " " + str(desc) + ", температурка " + str(
        temperature) + "°C, влажность - " + str(hum) + "%, скорость ветерка - " + str(wind) + "м/с.")


def get_translate_text(message):
    translate_text = message.text
    response = requests.get(
        'https://translate.yandex.net/api/v1.5/tr.json/translate',
        params={'key': KEYYANDEXTR,
                'text': translate_text,
                'lang': 'ru-en'})
    result = response.json()
    if result.get('code') != 200:
        class TranslateException(Exception):
            pass

        raise TranslateException(result.get('message'))
    bot.send_message(message.chat.id, result.get('text')[0])


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    duration = message.voice.duration
    if duration < 1:
        bot.send_message(message.chat.id, 'Голосовое сообщение слишком короткое.')
    elif duration > 3:
        bot.send_message(message.chat.id, 'Голосовое сообщение слишком длинное.')


@bot.message_handler(content_types=['document'])
def handle_docs_photo(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    src = 'C:/telegram_tutorial/' + message.document.file_name
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.reply_to(message, "Пожалуй, я сохраню это")


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    raw = message.photo[1].file_id
    path = raw + ".jpg"
    file_info = bot.get_file(raw)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(path, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.reply_to(message, "Фотография сохранена в \PycharmProjects\samcup")


# @bot.callback_query_handler(func=lambda call: call.data == "country")
# def callback_country(call):
#    keyboard = types.InlineKeyboardMarkup()
#    callback_button = types.InlineKeyboardButton(text="Россия", callback_data="ru")
#    keyboard.add(callback_button)
#    callback_button = types.InlineKeyboardButton(text="Украина", callback_data="ua")
#    keyboard.add(callback_button)
#    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери страну",
#                          reply_markup=keyboard)
# @bot.callback_query_handler(func=lambda call: call.data in ["ru", "ua"])
# def callback_country_choice(call):
#   bot.send_message(call.message.chat.id, "Вы выбрали %s" % call.data)

bot.polling(none_stop=True, interval=0)
