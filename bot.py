import logging
import os
import telebot
import time

from db_operations import UsersData
from nutrients_logic import NutrientsCalculator
from question_checker import get_user_question_name, set_next_question, question_checker
from yaml_util import load_yml_file

logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(os.getenv("NUTRITIVE_BOT_TOKEN"))
messages_base = load_yml_file("messages.yml")
nutrients_base = load_yml_file("nutrients.yml")
nutrients_calculator = NutrientsCalculator()
questions_base = load_yml_file("questions.yml")

def get_nutrient_norm_result(chat_id):
    with UsersData() as db:
        nutrient_name = db.get_user_nutrient(chat_id)
    if not nutrient_name:
        return messages_base["no_data_in_db"]
    answers = []
    if "questions" in nutrients_base[nutrient_name]:
        with UsersData() as db:
            answers = db.get_answers(chat_id, nutrients_base[nutrient_name]["questions"])
    for answer in answers:
        if not answer:
            return messages_base["no_data_in_db"]
    result = nutrients_calculator.calculate_norm(nutrient_name, answers)
    with UsersData() as db:
        db.set_user_nutrient(chat_id, None)
        db.set_user_question_index(chat_id, None)
    return result

@bot.message_handler(commands=["start", "help"])
def welcome_message(message):
    try:
        bot.reply_to(message, messages_base["welcome_message"], parse_mode="Markdown")
    except telebot.apihelper.ApiException as e:
        logging.error(e)

@bot.message_handler(commands=["list"])
def list_nutrients(message):
    width = messages_base["list_nutrients_row_width"]
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=width)
    nutrients = [(nutr["name"], nutr["symbol"]) for nutr in nutrients_base.values()]
    buttons = []
    for nutrient in nutrients:
        cur_button = telebot.types.InlineKeyboardButton(text=nutrient[0], callback_data=nutrient[1])
        buttons.append(cur_button)
    keyboard.add(*buttons)
    try:
        bot.send_message(chat_id=message.chat.id, text=messages_base["nutrients_list"], reply_markup=keyboard)
    except telebot.apihelper.ApiException as e:
        logging.error(e)

@bot.callback_query_handler(lambda call: call.data in nutrients_base)
def handle_nutrient_click(call):
    nutrient = call.data
    keyboard = telebot.types.InlineKeyboardMarkup()
    info_button = telebot.types.InlineKeyboardButton(text=messages_base["info_button"], callback_data="info {}".format(nutrient))
    calculate_button = telebot.types.InlineKeyboardButton(text=messages_base["calculate_button"], callback_data="calculate {}".format(nutrient))
    keyboard.add(info_button)
    keyboard.add(calculate_button)
    # TODO: Add "back to list" button
    try:
        bot.edit_message_text(text=messages_base["clicked_nutrient_text"].format(name=nutrients_base[nutrient]["name"]), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)
    except telebot.apihelper.ApiException as e:
        logging.error(e)

@bot.callback_query_handler(lambda call: call.data[:len("info")] == "info")
def handle_info_button(call):
    nutrient_name = call.data[len("info "):]
    assert nutrient_name in nutrients_base
    nutrient = nutrients_base[nutrient_name]
    info_text = messages_base["info_nutrient"].format(name=nutrient["name"], produced=nutrient["produced"], properties=nutrient["properties"])
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=info_text)
    except telebot.apihelper.ApiException as e:
        logging.error(e)

@bot.callback_query_handler(lambda call: call.data[:len("calculate")] == "calculate")
def handle_calculate_button(call):
    nutrient_name = call.data[len("calculate "):]
    chat_id = call.message.chat.id
    with UsersData() as db:
        db.set_user_nutrient(chat_id=chat_id, nutrient=nutrient_name)
        db.set_user_question_index(chat_id=chat_id, question_index=0)
    if (not "questions" in nutrients_base[nutrient_name]) or len(nutrients_base[nutrient_name]["questions"]) == 0:
        result = get_nutrient_norm_result(chat_id)
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=result)
        except telebot.apihelper.ApiException as e:
            logging.error(e)
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages_base["answer_questions"])
        first_question = nutrients_base[nutrient_name]["questions"][0]
        try:
            bot.send_message(call.message.chat.id, questions_base[first_question]["question_text"])
        except telebot.apihelper.ApiException as e:
            logging.error(e)

@bot.message_handler(func=lambda message: get_user_question_name(message.chat.id))
def answer_question(message):
    question_name = get_user_question_name(message.chat.id)
    assert question_name in question_checker
    response = question_checker[question_name](message.text)
    if response.status:
        with UsersData() as db:
            db.set_answer(chat_id=message.chat.id, question=question_name, value=response.result)
        if response.message:
            try:
                bot.reply_to(message, response.message)
            except telebot.apihelper.ApiException as e:
                logging.error(e)
        if set_next_question(message.chat.id):
            new_question = get_user_question_name(message.chat.id)
            try:
                bot.send_message(message.chat.id, new_question)
            except telebot.apihelper.ApiException as e:
                logging.error(e)
        else:
            result = get_nutrient_norm_result(message.chat.id)
            try:
                bot.send_message(message.chat.id, result)
            except telebot.apihelper.ApiException as e:
                logging.error(e)
    elif response.message:
        try:
            bot.reply_to(message, response.message)
        except telebot.apihelper.ApiException as e:
            logging.error(e)

@bot.message_handler(commands=["sun", "sunny"])
def with_love(message):
    try:
        bot.reply_to(message, "\u2600\ufe0fБот был придуман и разработан солнечной Сашей Морозовой и реализован её добрым коллегой Кириллом Сизовым\u2600\ufe0f")
    except telebot.apihelper.ApiException as e:
        logging.error(e)

@bot.message_handler(content_types=["text"])
def only_text(message):
    try:
        bot.reply_to(message, messages_base["no_commands_message"])
    except telebot.apihelper.ApiException as e:
        logging.error(e)


if __name__ == "__main__":
    bot.infinity_polling()