import argparse
import logging
import os
import telebot
import time

from db_operations import UsersData
from nutrients_logic import NutrientsCalculator
from question_checker import question_checker
from yaml_util import load_yml_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telergram bot for calculate nutrients norm")
    parser.add_argument("token", help="telegram bot token", type=str)
    parser.add_argument("database", help="path to database", type=str)
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)

    logging.info("Start executing")

    DB_LOCATION = args.database
    
    bot = telebot.TeleBot(token=args.token)

    logging.info("Connected to telegram bot")

    messages_base = load_yml_file("messages.yml")
    nutrients_base = load_yml_file("nutrients.yml")
    questions_base = load_yml_file("questions.yml")
    
    logging.info("Configs successfully loaded")

    nutrients_calculator = NutrientsCalculator()


def get_user_question_name(chat_id):
    with UsersData(DB_LOCATION) as db:
        nutrient = db.get_user_nutrient(chat_id)
        question_ind = db.get_user_question_index(chat_id)
    if (nutrient is None) or (question_ind is None):
        return None
    if nutrient not in nutrients_base:
        logging.error("There is no nutrients with name {} in base".format(nutrient))
        return None 
    if not "questions" in nutrients_base[nutrient]:
        return None
    if question_ind < 0 or question_ind >= len(nutrients_base[nutrient]["questions"]):
        logging.error("Invalid question index {} for nutrient {}".format(question_ind, nutrient))
        return None
    return nutrients_base[nutrient]["questions"][question_ind]


def set_next_question(chat_id):
    # here
    with UsersData(DB_LOCATION) as db:
        nutrient = db.get_user_nutrient(chat_id)
        question_ind = db.get_user_question_index(chat_id)
        if (nutrient is None) or (question_ind is None):
            logging.warn("Trying to set next question for user with current nutrient: {} and with question index: {}".format(nutrient, question_ind))
            return None
        if nutrient not in nutrients_base:
            logging.error("There is no nutrients with name {} in base".format(nutrient))
            return None 
        if not "questions" in nutrients_base[nutrient]:
            return None
        if question_ind < 0 or question_ind >= len(nutrients_base[nutrient]["questions"]):
            logging.warn("Trying to set next question with incorrect index {} for nutrient {}".format(question_ind, nutrient))
            return None
        question_ind += 1
        if question_ind < len(nutrients_base[nutrient]["questions"]):
            db.set_user_question_index(chat_id, question_ind)

            # skiping pregnant question if man`s gender is male
            cur_question_name = get_user_question_name(chat_id)
            if cur_question_name == 'pregnant':
                gender = db.get_answers(chat_id, ['gender'])['gender']
                if gender and gender == 1:
                    db.set_answer(chat_id, 'pregnant', 0)
                    question_ind += 1
                    if question_ind < 0 or question_ind >= len(nutrients_base[nutrient]["questions"]):
                        return None
                    db.set_user_question_index(chat_id, question_ind)
            return True
        return False


def get_nutrient_norm_result(chat_id):
    with UsersData(DB_LOCATION) as db:
        nutrient_name = db.get_user_nutrient(chat_id)
    if not nutrient_name:
        return messages_base["no_data_in_db"]
    answers = []
    if "questions" in nutrients_base[nutrient_name]:
        with UsersData(DB_LOCATION) as db:
            answers = db.get_answers(chat_id, nutrients_base[nutrient_name]["questions"])
    if answers:
        for answer in answers.values():
            if answer is None:
                with UsersData(DB_LOCATION) as db:
                    db.set_user_nutrient(chat_id, None)
                    db.set_user_question_index(chat_id, None)
                return messages_base["no_data_in_db"]
    result = nutrients_calculator.calculate_norm(nutrient_name, answers)
    with UsersData(DB_LOCATION) as db:
        db.set_user_nutrient(chat_id, None)
        db.set_user_question_index(chat_id, None)
    return result

def ask_question(chat_id):
    question_name = get_user_question_name(chat_id)
    assert question_name in questions_base
    question = questions_base[question_name]
    if "answers" in question:
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for answer in question["answers"]:
            button = telebot.types.KeyboardButton(text=answer)
            keyboard.add(button)
        try:
            bot.send_message(chat_id=chat_id, text=question["question_text"], reply_markup=keyboard)
        except telebot.apihelper.ApiException as e:
            logging.error(e)
    else:
        erase_keyboard = telebot.types.ReplyKeyboardRemove(selective=False)
        try:
            bot.send_message(chat_id=chat_id, text=question["question_text"], reply_markup=erase_keyboard)
        except telebot.apihelper.ApiException as e:
            logging.error(e)

def get_main_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=messages_base["main_keyboard_row_width"], resize_keyboard=True)
    nutrients_list_button = telebot.types.KeyboardButton(text=messages_base["nutrients_list_button"])
    about_us_button = telebot.types.KeyboardButton(text=messages_base["about_us_button"])
    keyboard.add(nutrients_list_button, about_us_button)
    return keyboard

def get_nutrients_list_keyboard():
    width = messages_base["list_nutrients_row_width"]
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=width)
    nutrients = [(nutr["name"], nutr["symbol"]) for nutr in nutrients_base.values()]
    buttons = []
    for nutrient in nutrients:
        cur_button = telebot.types.InlineKeyboardButton(text=nutrient[0], callback_data=nutrient[1])
        buttons.append(cur_button)
    keyboard.add(*buttons)
    return keyboard    

@bot.message_handler(commands=["start", "help"])
def welcome_message(message):
    try:
        bot.send_message(message.chat.id, messages_base["welcome_message"], parse_mode="Markdown", reply_markup=get_main_keyboard())
        bot.send_message(message.chat.id, messages_base["warning_message"], parse_mode="Markdown", reply_markup=get_main_keyboard())
    except telebot.apihelper.ApiException as e:
        logging.error(e)

@bot.callback_query_handler(lambda call: call.data in nutrients_base)
def handle_nutrient_click(call):
    nutrient = call.data
    keyboard = telebot.types.InlineKeyboardMarkup()
    info_button = telebot.types.InlineKeyboardButton(text=messages_base["info_button"], callback_data="info {}".format(nutrient))
    calculate_button = telebot.types.InlineKeyboardButton(text=messages_base["calculate_button"], callback_data="calculate {}".format(nutrient))
    back_button = telebot.types.InlineKeyboardButton(text=messages_base["back_to_list_button"], callback_data="back_to_list")
    keyboard.add(info_button)
    keyboard.add(calculate_button)
    keyboard.add(back_button)
    try:
        bot.edit_message_text(text=messages_base["clicked_nutrient_text"].format(name=nutrients_base[nutrient]["name"]), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
    except telebot.apihelper.ApiException as e:
        logging.error(e)

@bot.callback_query_handler(lambda call: call.data == "back_to_list") 
def handle_back_to_list(call):
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=messages_base["nutrients_list"],
            reply_markup=get_nutrients_list_keyboard()
        )
    except telebot.apihelper.ApiException as e:
        logging.error(e)

@bot.callback_query_handler(lambda call: call.data[:len("info")] == "info")
def handle_info_button(call):
    nutrient_name = call.data[len("info "):]
    assert nutrient_name in nutrients_base
    keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text=messages_base["back_to_nutrient"], callback_data=nutrient_name)
    keyboard.add(back_button)
    nutrient = nutrients_base[nutrient_name]
    info_text = messages_base["info_nutrient"].format(name=nutrient["name"], produced=nutrient["produced"], properties=nutrient["properties"])
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=info_text, reply_markup=keyboard)
    except telebot.apihelper.ApiException as e:
        logging.error(e)

@bot.callback_query_handler(lambda call: call.data[:len("calculate")] == "calculate")
def handle_calculate_button(call):
    nutrient_name = call.data[len("calculate "):]
    chat_id = call.message.chat.id
    with UsersData(DB_LOCATION) as db:
        db.set_user_nutrient(chat_id=chat_id, nutrient=nutrient_name)
        db.set_user_question_index(chat_id=chat_id, question_index=0)
    if (not "questions" in nutrients_base[nutrient_name]) or len(nutrients_base[nutrient_name]["questions"]) == 0:
        result = get_nutrient_norm_result(chat_id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        back_button = telebot.types.InlineKeyboardButton(text=messages_base["back_to_nutrient"], callback_data=nutrient_name)
        keyboard.add(back_button)
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id, 
                message_id=call.message.message_id, 
                text=result,
                reply_markup=keyboard
            )
        except telebot.apihelper.ApiException as e:
            logging.error(e)
    else:
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages_base["answer_questions"])
        except telebot.apihelper.ApiException as e:
            logging.error(e)
        ask_question(chat_id)

@bot.message_handler(func=lambda message: get_user_question_name(message.chat.id))
def answer_question(message):
    question_name = get_user_question_name(message.chat.id)
    assert question_name in question_checker
    response = question_checker[question_name](message.text)
    if response.status:
        with UsersData(DB_LOCATION) as db:
            db.set_answer(chat_id=message.chat.id, question=question_name, value=response.result)
        if response.message:
            try:
                bot.reply_to(message, response.message)
            except telebot.apihelper.ApiException as e:
                logging.error(e)
        if set_next_question(message.chat.id):
            ask_question(message.chat.id)
        else:
            result = get_nutrient_norm_result(message.chat.id)
            try:
                bot.send_message(chat_id=message.chat.id, text=result, reply_markup=get_main_keyboard())
            except telebot.apihelper.ApiException as e:
                logging.error(e)
    elif response.message:
        try:
            bot.reply_to(message, response.message)
        except telebot.apihelper.ApiException as e:
            logging.error(e)

@bot.message_handler(func=lambda message: message.text == messages_base["nutrients_list_button"])
def list_nutrients(message):
    try:
        bot.send_message(chat_id=message.chat.id, text=messages_base["nutrients_list"], reply_markup=get_nutrients_list_keyboard())
    except telebot.apihelper.ApiException as e:
        logging.error(e)

@bot.message_handler(func=lambda message: message.text == messages_base["about_us_button"])
def about_us(message):
    bot.send_message(chat_id=message.chat.id, text=messages_base["about_us"], parse_mode="Markdown")


@bot.message_handler(content_types=["text"])
def only_text(message):
    try:
        bot.reply_to(message, messages_base["no_commands_message"])
    except telebot.apihelper.ApiException as e:
        logging.error(e)


if __name__ == "__main__":
    logging.info("Start polling")
    bot.polling(none_stop=False)
