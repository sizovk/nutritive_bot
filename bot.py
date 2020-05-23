import logging
import os
import telebot

from db_operations import UsersData
from nutrients_logic import NutrientsCalculator
from question_checker import get_user_question_name, set_next_question, question_checker
from yaml_util import load_yml_file

bot = telebot.TeleBot(os.getenv("NUTRITIVE_BOT_TOKEN"))
messages_base = load_yml_file("messages.yml")
nutrients_base = load_yml_file("nutrients.yml")
nutrients_calculator = NutrientsCalculator()
questions_base = load_yml_file("questions.yml")

@bot.message_handler(commands=["start", "help"])
def welcome_message(message):
    bot.reply_to(message, messages_base["welcome_message"], parse_mode="Markdown")

@bot.message_handler(commands=["all"])
def all_nutrients(message):
    index = 1
    nutrients_list = []
    for name, data in nutrients_base.items():
        nutrients_list.append(messages_base["nutrients_list_item"].format(index=index, name=data["name"], symbol=data["symbol"]))
        index += 1
    bot.reply_to(message, messages_base["all_nutrients"].format(nutrients_list="".join(nutrients_list)))

@bot.message_handler(commands=["info"])
def info_nutrient(message):
    given_text = message.text[len("/info "):]
    if given_text in nutrients_base:
        nutr = nutrients_base[given_text] 
        bot.reply_to(message, messages_base["info_nutrient"].format(name=nutr["name"], symbol=nutr["symbol"], produced=nutr["produced"], properties=nutr["properties"]))
    else:
        bot.reply_to(message, messages_base["no_nutrient_with_given_symbol"])

@bot.message_handler(commands=["calculate"])
def set_calculate_state(message):
    cur_question = get_user_question_name(message.chat.id)
    if cur_question:
        bot.reply_to(message, messages_base["finish_form_before_start_new_one"])
        bot.send_message(message, questions_base[cur_question]["question_text"])
        return
    given_text = message.text[len("/calculate "):]
    if given_text in nutrients_base:
        nutrient = given_text
        with UsersData() as db:
            db.set_user_nutrient(message.chat.id, nutrient)
            db.set_user_question_index(message.chat.id, 0)
        if (not "questions" in nutrients_base[nutrient]) or len(nutrients_base[nutrient]["questions"]) == 0:
            calculate_nutrient_norm(message.chat.id)
        else:
            first_question = nutrients_base[nutrient]["questions"][0]
            bot.send_message(message.chat.id, questions_base[first_question]["question_text"])
    else:
        bot.reply_to(message, messages_base["no_nutrient_with_given_symbol"])

def calculate_nutrient_norm(chat_id):
    with UsersData() as db:
        nutrient = db.get_user_nutrient(chat_id)
        if not nutrient:
            bot.send_message(chat_id, messages_base["no_data_in_db"])
            return
        if "questions" in nutrients_base[nutrient]:
            answers = db.get_answers(chat_id, nutrients_base[nutrient]["questions"])
        else:
            answers = []
        for answer in answers:
            if not answer:
                bot.send_message(chat_id, messages_base["no_data_in_db"])
                return
        result_message = nutrients_calculator.calculate_norm(nutrient, answers)
        bot.send_message(chat_id, result_message)
        db.set_user_nutrient(chat_id, None)
        db.set_user_question_index(chat_id, None)

@bot.message_handler(func=lambda message: get_user_question_name(message.chat.id))
def answer_question(message):
    question_name = get_user_question_name(message.chat.id)
    assert question_name in question_checker
    response = question_checker[question_name](message.text)
    if response.status:
        with UsersData() as db:
            db.set_answer(chat_id=message.chat.id, question=question_name, value=response.result)
        if response.message:
            bot.reply_to(message, response.message)
        if set_next_question(message.chat.id):
            new_question = get_user_question_name(message.chat.id)
            bot.send_message(message.chat.id, new_question)
        else:
            calculate_nutrient_norm(message.chat.id)
    elif response.message:
        bot.reply_to(message, response.message)

@bot.message_handler(commands=["sun", "sunny"])
def with_love(message):
    bot.reply_to(message, "\u2600\ufe0fБот был придуман и разработан солнечной Саней Морозовой и реализован её добрым коллегой Кириллом Сизовым\u2600\ufe0f")

@bot.message_handler(content_types=["text"])
def only_text(message):
    bot.reply_to(message, messages_base["no_commands_message"])


if __name__ == "__main__":
    bot.infinity_polling()