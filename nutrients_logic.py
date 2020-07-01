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
            Nutrient.Se.value: selen,
            Nutrient.Zn.value: zinc,
            Nutrient.Mg.value: magnesium,
            Nutrient.Ca.value: calcium,
            Nutrient.I.value: iodine,
            Nutrient.Fe.value: ferrum,
            Nutrient.C.value: vitamin_c,
            Nutrient.VP.value: vitamin_p,
            Nutrient.E.value: vitamin_e
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
    if answers[Question.AGE.value] >= 18:
        return cur_results["adult"]
    return cur_results["child"]

def selen(answers):
    results = nutrients_base[Nutrient.Se.value]["results"]
    if answers[Question.AGE.value] < 18:
        return results["child"]
    if answers[Question.GENDER.value]:
        return results["man"]
    return results["woman"]

def zinc(answers):
    results = nutrients_base[Nutrient.Zn.value]["results"]
    age = answers[Question.AGE.value]  
    if age >= 18:
        if answers[Question.GENDER.value]:
            return results["man"]
        else:
            return results["woman"]
    elif age < 1:
        return results["age_0_0"]
    elif age < 3:
        return results["age_1_3"]
    elif age < 7:
        return results["age_3_7"]
    elif age < 11:
        return results["age_7_11"]
    elif age < 18:
        return results["age_11_18"]

def magnesium(answers):
    results = nutrients_base[Nutrient.Mg.value]["results"]
    age = answers[Question.AGE.value]
    if age >= 18:
        if answers[Question.GENDER.value]:
            return results["man"]
        else:
            return results["woman"]
    elif age < 1:
        return results["age_0_0"]
    elif age < 4:
        return results["age_1_4"]
    elif age < 7:
        return results["age_4_7"]
    elif age < 11:
        return results["age_7_11"]
    elif age < 15:
        return results["age_11_15"]
    elif age < 18:
        return results["age_15_18"]

def calcium(answers):
    results = nutrients_base[Nutrient.Ca.value]["results"]
    age = answers[Question.AGE.value]
    if answers[Question.PREGNANT.value]:
        return results["pregnant"]
    elif age < 1:
        return results["age_0_0"]
    elif age < 3:
        return results["age_1_3"]
    elif age < 11:
        return results["age_3_11"]
    elif age < 18:
        return results["age_11_18"]
    elif age < 60:
        return results["age_18_60"]
    else:
        return results["age_60+"]

def iodine(answers):
    results = nutrients_base[Nutrient.I.value]["results"]
    age = answers[Question.AGE.value]
    if age < 6:
        return results["age_0_6"]
    elif age < 12:
        return results["age_6_12"]
    elif answers[Question.GENDER.value]:
        return results["man_12+"]
    else:
        return results["woman_12+"]

def ferrum(answers):
    results = nutrients_base[Nutrient.Fe.value]["results"]
    age = answers[Question.AGE.value]
    if age < 1:
        return results["age_0_0"]
    elif age < 15:
        return results["age_1_15"]
    elif age < 18:
        if answers[Question.GENDER.value]:
            return results["man_15_18"]
        else:
            return results["woman_15_18"]
    elif answers[Question.GENDER.value]:
        return results["man_18+"]
    else:
        return results["woman_18+"]

def vitamin_c(answers):
    results = nutrients_base[Nutrient.C.value]["results"]
    age = answers[Question.AGE.value]
    if answers[Question.PREGNANT.value]:
        return results["pregnant"]
    elif age < 15:
        return results["age_0_15"]
    elif age < 18:
        return results["age_15_18"]
    else:
        return results["age_18+"]

def vitamin_p(answers):
    results = nutrients_base[Nutrient.VP.value]["results"]
    if answers[Question.SPORT.value]:
        return results["sport"]
    elif answers[Question.AGE.value] < 18:
        return results["child"]
    else:
        return results["adult"]

def vitamin_e(answers):
    template = nutrients_base[Nutrient.E.value]["results"]["template"]
    if answers[Question.AGE.value] == 0:
        norm = answers[Question.WEIGHT.value] * 0.5
    else:
        norm = answers[Question.WEIGHT.value] * 0.3
    return template.format(count=norm)