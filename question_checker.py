import logging

from config import Question
from db_operations import UsersData
from yaml_util import load_yml_file

nutrients_base = load_yml_file("nutrients.yml")
questions_base = load_yml_file("questions.yml")

class CheckerResponse:
    def __init__(self, message=None, result=None, status=False):
        self.message = message
        self.result = result
        self.status = status


def get_user_question_name(chat_id):
    with UsersData() as db:
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
    with UsersData() as db:
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
            return True
        return False


def how_old(answer):
    question_messages = questions_base[Question.HOW_OLD.value]
    result = convert_to_int(answer)
    if result is None:
        return CheckerResponse(message=question_messages["not_number"])
    if result < 0:
        return CheckerResponse(message=question_messages["neg_number"])
    return CheckerResponse(result=result, status=True)

question_checker = {
    Question.HOW_OLD.value: how_old
}


def convert_to_int(text):
    try:
        return int(text)
    except:
        return None



    
        
        