import logging
import sqlite3

import config

class UsersData:
    def __init__(self, db_location=config.DB_LOCATION):
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
            chat_id integer,
            current_nutrient text,
            question_index integer,
            age integer
        )""")
        self.commit()

    def get_fields_by_chat_id(self, chat_id, fields: tuple):
        fields_repr = ", ".join(fields)
        sql_query = "SELECT {} FROM Users WHERE chat_id=?".format(fields_repr)
        self.__db_cursor.execute(sql_query, (chat_id,))
        return self.__db_cursor.fetchall()

