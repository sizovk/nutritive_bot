import logging
import sqlite3


class UsersData:
    def __init__(self, db_location):
        self.__DB_LOCATION = db_location
        self.__db_connection = sqlite3.connect(self.__DB_LOCATION)
        self.__db_cursor = self.__db_connection.cursor()
        self.__create_table_if_not_exists()
    
    def __del__(self):
        self.__db_connection.close()

    def __enter__(self):
        return self
    
    def __exit__(self, ext_type, exc_value, traceback):
        self.__db_cursor.close()
        if isinstance(exc_value, Exception):
            self.__db_connection.rollback()
        else:
            self.__db_connection.commit()
        self.__db_connection.close()
    
    def close(self):
        self.__db_connection.close()

    def commit(self):
        self.__db_connection.commit()
    
    def __create_table_if_not_exists(self):
        self.__db_cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
            chat_id INTEGER NOT NULL UNIQUE,
            current_nutrient TEXT,
            question_index INTEGER
        )""")
        self.__db_cursor.execute("""CREATE TABLE IF NOT EXISTS Answers(
            chat_id INTEGER NOT NULL UNIQUE,
            age INTEGER,
            gender BOOLEAN,
            pregnant BOOLEAN,
            sport BOOLEAN,
            weight REAL
        )""")
        self.commit()

    def __insert_user_if_not_in_db(self, chat_id):
        self.__db_cursor.execute("INSERT OR IGNORE INTO Users(chat_id) VALUES(?)", (chat_id,))
        self.__db_cursor.execute("INSERT OR IGNORE INTO Answers(chat_id) VALUES(?)", (chat_id,))

    def get_user_nutrient(self, chat_id):
        self.__insert_user_if_not_in_db(chat_id)
        self.__db_cursor.execute("SELECT current_nutrient FROM Users WHERE chat_id=?", (chat_id,))
        items = self.__db_cursor.fetchall()
        return items[0][0]

    def set_user_nutrient(self, chat_id, nutrient):
        self.__insert_user_if_not_in_db(chat_id)
        self.__db_cursor.execute("UPDATE Users SET current_nutrient=? WHERE chat_id=?", (nutrient, chat_id))
        self.commit()

    def get_user_question_index(self, chat_id):
        self.__insert_user_if_not_in_db(chat_id)
        self.__db_cursor.execute("SELECT question_index FROM Users WHERE chat_id=?", (chat_id,))
        items = self.__db_cursor.fetchall()
        return items[0][0]
    
    def set_user_question_index(self, chat_id, question_index):
        self.__insert_user_if_not_in_db(chat_id)
        self.__db_cursor.execute("UPDATE Users SET question_index=? WHERE chat_id=?", (question_index, chat_id))
        self.commit()
    
    def get_answer(self, chat_id, question):
        self.__insert_user_if_not_in_db(chat_id)
        self.__db_cursor.execute("SELECT {} FROM Answers WHERE chat_id=?".format(question), (chat_id,))
        items = self.__db_cursor.fetchall()
        return items[0][0]

    def get_answers(self, chat_id, questions):
        self.__insert_user_if_not_in_db(chat_id)
        questions_repr = ", ".join(questions)
        self.__db_cursor.execute("SELECT {} FROM Answers WHERE chat_id=?".format(questions_repr), (chat_id,))
        answers_tuple = self.__db_cursor.fetchall()[0]
        answers_dict = dict()
        assert len(questions) == len(answers_tuple)
        for i in range(len(questions)):
            answers_dict[questions[i]] = answers_tuple[i]
        return answers_dict

    def set_answer(self, chat_id, question, value):
        self.__insert_user_if_not_in_db(chat_id)
        self.__db_cursor.execute("UPDATE Answers SET {}=? WHERE chat_id=?".format(question), (value, chat_id))
        self.commit()
