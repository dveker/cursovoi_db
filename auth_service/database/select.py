from database.DBcm import DBContextManager
from flask import current_app  # глобальная переменная которая содержит все глобальные параметры


def select_list(db_config, _sql: str, param_list: list) -> tuple:
    with DBContextManager(db_config) as cursor:
        if cursor is None:  # Удалось ли подключиться?
            raise ValueError('Не удалось подключиться!')  # Генерирует фиктивную ошибку
        else:
            if param_list:
                cursor.execute(_sql, param_list)
            else:
                cursor.execute(_sql)
            result = cursor.fetchall()
            schema = []
            for item in cursor.description:
                schema.append(item[0])
            print(schema)
            return result, schema


def select_dict(db_config, _sql: str, user_dict: dict):
    user_list = []
    for key in user_dict:
        user_list.append(user_dict[key])
    print('user_list in select_dict=', user_list)
    result_schema = select_list(db_config, _sql, user_list)
    if result_schema is None:
        return None
    result, schema = result_schema
    result_dict = []
    for item in result:
        result_dict.append(dict(zip(schema, item)))
    print(result_dict)
    return result_dict