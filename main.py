import telebot
from googletrans import Translator
from sqlalchemy.orm import Session
from telebot import types

from models import db_worker, Language, Word

translator = Translator()

bot = telebot.TeleBot("your bot telegram token")

"""greeting_discription welcomes the user also ask language also registr user to db if not ask a list of wrods from 
user"""


@bot.message_handler(commands=['start'])
@db_worker.with_db
def greeting_description(message, **kwargs):
    bot.send_message(message.chat.id, "Hello, I am VocabBoost I will help you increase your vocab")
    user_id = message.from_user.id
    db: Session = kwargs["db"]
    print(message)
    if not db.get(Language, user_id):
        bot.send_message(message.chat.id,
                         f"Now please send me first the language that you want to learn and language that"
                         f" is your native in form like: EN/RU that means you want to translate words from "
                         f"english to  Russian")
        bot.register_next_step_handler(message, set_language)  # handle message inside the translate_for_user
    else:
        bot.send_message(message.chat.id, "Please enter a list of words that you need to translate splitted by ','")
        bot.register_next_step_handler(message, translate_for_user)  # handle message inside the translate_for_user


"""Handle message and store it in db"""


@db_worker.with_db
def set_language(message, **kwargs):
    user_id = message.from_user.id
    db: Session = kwargs["db"]
    languages = message.text.strip().split("/")
    language = Language(id=user_id, source=languages[0], destination=languages[1])
    db.add(language)
    db.commit()
    bot.send_message(message.chat.id, "Please enter a list of words that you need to translate splitted by ','")
    bot.register_next_step_handler(message, translate_for_user)


#@bot.message_handler(commands=['Show the list'])
#def show_the_list(message):
#    on_click(message)

"""store the user list of words in table words also using library googletrans translate the words on destination 
language, also adds a buttons"""
@db_worker.with_db
def translate_for_user(message, **kwargs):
    user_id = message.from_user.id
    db: Session = kwargs["db"]
    language = db.get(Language, user_id)
    list_of_words_nt = message.text
    list_of_words_nt = [word.strip() for word in list_of_words_nt.split(',')]
    list_of_words_nt = [element.lower() for element in list_of_words_nt]

    if len(list_of_words_nt) >= 1:
        try:
            translations = translator.translate(list_of_words_nt, src=language.source, dest=language.destination)
        except Exception:
            bot.send_message(message.chat.id, "Please check that your language and words are written right")
            bot.register_next_step_handler(message, set_language)
            return
        mapped_words = list(zip(list_of_words_nt, translations))
        bot.send_message(message.chat.id,
                         '\n'.join(f"{x} - {y.text}" for x, y in mapped_words))
        a = set(word.source for word in language.words)
        words = [Word(user_id=user_id, source=src, destination=dst.text) for src, dst in mapped_words if src not in a]
        db.add_all(words)
        db.commit()
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton("Show the list")
        markup.row(btn1)
        btn2 = types.KeyboardButton("Change language")
        btn3 = types.KeyboardButton("Change time")
        markup.row(btn2, btn3)
        bot.send_message(message.chat.id, "Now in what time you prefer remember the words", reply_markup=markup)
        bot.register_next_step_handler(message, on_click)
    else:
        bot.send_message(message.chat.id, "Please enter the words")
        bot.register_next_step_handler(message, set_language)

"""Handle pressed buttons"""
@db_worker.with_db
def on_click(message, **kwargs):
    user_id = message.from_user.id
    db: Session = kwargs["db"]
    button_name = message.text
    if button_name == "Show the list":
        language = db.get(Language, user_id)
        mapped_words = '\n'.join([f"{word.source}-{word.destination}" for word in language.words])
        bot.send_message(message.chat.id, f"Languages are: {language.source}/{language.destination}\n"
                                          f"Your words are:\n{mapped_words}")
    elif button_name == "Change language":
        bot.register_next_step_handler(message, set_language)
    elif button_name == "Change time":
        pass


"""Here must be part with setting timer like in what time user prefer to get the reminds with list of words and 
then maybe implemented quizzes"""

bot.polling(none_stop=True)
