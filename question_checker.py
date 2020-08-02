import logging

from config import Question
from yaml_util import load_yml_file

nutrients_base = load_yml_file("nutrients.yml")
questions_base = load_yml_file("questions.yml")

class CheckerResponse:
    def __init__(self, message=None, result=None, status=False):
        self.message = message
        self.result = result
        self.status = status


def convert_to_int(text):
    try:
        return int(text)
    except ValueError:
        return None

def convert_to_float(text):
    try:
        return float(text)
    except ValueError:
        return None

def how_old(answer):
    question_messages = questions_base[Question.AGE.value]
    result = convert_to_int(answer)
    if result is None:
        return CheckerResponse(message=question_messages["not_number"])
    if result < 0:
        return CheckerResponse(message=question_messages["neg_number"])
    return CheckerResponse(result=result, status=True)

def get_gender(answer):
    question = questions_base[Question.GENDER.value]
    if not answer in question["answers"]:
        return CheckerResponse(message=question["wrong_format"])
    result = False
    if answer == question["answers"][0]:
        result = True
    return CheckerResponse(result=result, status=True)

def is_pregnant(answer):
    question = questions_base[Question.PREGNANT.value]
    if not answer in question["answers"]:
        return CheckerResponse(message=question["wrong_format"])
    result = False
    if answer == question["answers"][0]:
        result = True
    return CheckerResponse(result=result, status=True)

def do_sport(answer):
    question = questions_base[Question.SPORT.value]
    if not answer in question["answers"]:
        return CheckerResponse(message=question["wrong_format"])
    result = False
    if answer == question["answers"][0]:
        result = True
    return CheckerResponse(result=result, status=True)

def get_weight(answer):
    question = questions_base[Question.WEIGHT.value]
    result = convert_to_float(answer)
    if result is None:
        return CheckerResponse(message=question["not_number"])
    if result < 0:
        return CheckerResponse(message=question["neg_number"])
    return CheckerResponse(result=result, status=True)

question_checker = {
    Question.AGE.value: how_old,
    Question.GENDER.value: get_gender,
    Question.PREGNANT.value: is_pregnant,
    Question.SPORT.value: do_sport,
    Question.WEIGHT.value: get_weight
}        
        