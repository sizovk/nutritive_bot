import logging

from config import Question, Nutrient
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
            Nutrient.E.value: vitamin_e,
            Nutrient.B9.value: vitamin_b9,
            Nutrient.B4.value: vitamin_b4,
            Nutrient.B6.value: vitamin_b6,
            Nutrient.B3.value: vitamin_b3,
            Nutrient.B2.value: vitamin_b2,
            Nutrient.B1.value: vitamin_b1,
            Nutrient.A.value: vitamin_a,
            Nutrient.L.value: l_karnitin,
            Nutrient.VK.value: vitamin_k,
            Nutrient.B13.value: vitamin_b13,
            Nutrient.B12.value: vitamin_b12,
            Nutrient.D.value: vitamin_d
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

def vitamin_b9(answers):
    results = nutrients_base[Nutrient.B9.value]["results"]
    age = answers[Question.AGE.value]
    if answers[Question.PREGNANT.value]:
        return results["pregnant"]
    elif age < 1:
        return results["age_0_1"]
    elif age < 3:
        return results["age_1_3"]
    elif age < 11:
        return results["age_3_11"]
    elif age < 14:
        return results["age_11_14"]
    else:
        return results["age_14+"]

def vitamin_b4(answers):
    results = nutrients_base[Nutrient.B4.value]["results"]
    age = answers[Question.AGE.value]
    if age < 1:
        return results["age_0_1"]
    elif age < 3:
        return results["age_1_3"]
    elif age < 7:
        return results["age_3_7"]
    elif age < 18:
        return results["age_7_18"]
    else:
        return results["age_18+"]

def vitamin_b6(answers):
    results = nutrients_base[Nutrient.B6.value]["results"]
    age = answers[Question.AGE.value]
    if age < 1:
        return results["age_0_1"]
    elif age < 6:
        return results["age_1_6"]
    elif age < 10:
        return results["age_6_10"]
    else:
        return results["age_10+"]

def vitamin_b3(answers):
    results = nutrients_base[Nutrient.B3.value]["results"]
    age = answers[Question.AGE.value]
    if age < 1:
        return results["age_0_1"]
    elif age < 6:
        return results["age_1_6"]
    else:
        return results["age_6+"]

def vitamin_b2(answers):
    results = nutrients_base[Nutrient.B2.value]["results"]
    age = answers[Question.AGE.value]
    if answers[Question.PREGNANT.value]:
        return results["pregnant"]
    elif age < 1:
        return results["age_0_1"]
    elif age < 4:
        return results["age_1_4"]
    elif age < 9:
        return results["age_4_9"]
    elif age < 14:
        if answers[Question.GENDER.value]:
            return results["man_9_14"]
        else:
            return results["woman_9_14"]
    else:
        if answers[Question.GENDER.value]:
            return results["man_14+"]
        else:
            return results["woman_14+"]

def vitamin_b1(answers):
    results = nutrients_base[Nutrient.B1.value]["results"]
    age = answers[Question.AGE.value]
    if answers[Question.PREGNANT.value]:
        return results["pregnant"]
    elif age < 3:
        return results["age_0_3"]
    elif age < 14:
        return results["age_3_14"]
    elif age < 18:
        return results["age_14_18"]
    elif age < 50:
        if answers[Question.GENDER.value]:
            return results["man_18_50"]
        else:
            return results["woman_18_50"]
    else:
        return results["age_50+"]

def vitamin_a(answers):
    results = nutrients_base[Nutrient.A.value]["results"]
    if answers[Question.PREGNANT.value]:
        return results["pregnant"]
    if answers[Question.AGE.value] < 18:
        return results["child"]
    if answers[Question.GENDER.value]:
        return results["man"]
    return results["woman"]

def l_karnitin(answers):
    results = nutrients_base[Nutrient.L.value]["results"]
    age = answers[Question.AGE.value]
    if age < 1:
        return results["age_0_1"]
    elif age < 4:
        return results["age_1_4"]
    elif age < 7:
        return results["age_4_7"]
    elif age < 18:
        return results["age_7_18"]
    elif answers[Question.SPORT.value]:
        return results["sport"]
    else:
        return results["age_18+"]

def vitamin_k(answers):
    results = nutrients_base[Nutrient.VK.value]["results"]
    age = answers[Question.AGE.value]
    if age < 1:
        return results["age_0_1"]
    if age < 4:
        return results["age_1_4"]
    if age < 9:
        return results["age_4_9"]
    if age < 14:
        return results["age_9_14"]
    if age < 19:
        return results["age_14_19"]
    else:
        return results["age_19+"]    

def vitamin_b13(answers):
    results = nutrients_base[Nutrient.B13.value]["results"]
    age = answers[Question.AGE.value]
    if answers[Question.PREGNANT.value]:
        return results["pregnant"]
    elif age < 1:
        return results["age_0_1"]
    elif age < 3:
        return results["age_1_3"]
    elif age < 8:
        return results["age_3_8"]
    else:
        return results["age_8+"]

def vitamin_b12(answers):
    results = nutrients_base[Nutrient.B12.value]["results"]
    age = answers[Question.AGE.value]
    if answers[Question.PREGNANT.value]:
        return results["pregnant"]
    elif age < 1:
        return results["age_0_1"]
    elif age < 4:
        return results["age_1_4"]
    elif age < 9:
        return results["age_4_9"]
    elif age < 14:
        return results["age_9_14"]
    else:
        return results["age_14+"]

def vitamin_d(answers):
    results = nutrients_base[Nutrient.D.value]["results"]
    age = answers[Question.AGE.value]
    if answers[Question.PREGNANT.value]:
        return results["pregnant"]
    elif age < 1:
        return results["age_0_1"]
    elif age < 14:
        return results["age_1_14"]
    elif age < 71:
        return results["age_14_71"]
    else:
        return results["age_71+"]
