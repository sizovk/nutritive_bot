import logging

from config import Question, Nutrient
from db_operations import UsersData
from yaml_util import load_yml_file

messages_base = load_yml_file("messages.yml")
nutrients_base = load_yml_file("nutrients.yml")

class NutrientsCalculator:
    def __init__(self):
        self.__dispatcher = {
            Nutrient.N.value: vitamin_n,
        }

    def calculate_norm(self, nutrient, answers):
        for answer in answers:
            assert(answer)
        if nutrient in self.__dispatcher:
            return self.__dispatcher[nutrient](answers)
        if "results" in nutrients_base[nutrient] and "default" in nutrients_base[nutrient]["results"]:
            return nutrients_base[nutrient]["results"]["default"]
        logging.warn("Can't find norm for nutrient {}".format(nutrient))
        return messages_base["not_added_calculate_func_for_nutrient"]

def vitamin_n(answers):
    cur_results = nutrients_base[Nutrient.N.value]["results"]
    if answers[Question.HOW_OLD.value] >= 18:
        return cur_results["adult"]
    else:
        return cur_results["child"]
