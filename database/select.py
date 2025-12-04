from cursach2.database.DBcm import DBContextManager
from flask import current_app



def select_list(_sql: str, param_list: list) -> tuple:
    print(f"SQL: {_sql}")
    print(f"Params: {param_list}")

    with DBContextManager(current_app.config['db_config']) as cursor:
        if cursor is None:
            print("Курсор не создан")
            raise ValueError('Не удалось подключиться')
        else:
            cursor.execute(_sql, param_list)
            result = cursor.fetchall()
            print(f"DB result: {result}")
            print(f"DB result length: {len(result) if result else 0}")
            return result


def select_dict(_sql, user_input: dict) -> list:

    user_list = []
    for key in user_input:
        user_list.append(user_input[key])
    print(f"User list for SQL: {user_list}")

    try:
        with DBContextManager(current_app.config['db_config']) as cursor:
            if cursor is None:
                print("Курсор не создан")
                raise ValueError('Не удалось подключиться')


            cursor.execute(_sql, user_list)


            description = cursor.description
            if description:
                column_names = [col[0] for col in description]
            else:
                column_names = []


            rows = cursor.fetchall()


            result = []
            for row in rows:
                row_dict = {}
                for i, col_name in enumerate(column_names):
                    if i < len(row):
                        row_dict[col_name] = row[i]
                result.append(row_dict)

            print(f"Dict result: {result}")
            print(f"Dict result length: {len(result)}")
            return result

    except Exception as e:
        print(f"Error in select_dict: {e}")
        return []


def execute_sql(_sql: str, param_list: list) -> bool:
    print(f"Execute SQL: {_sql}")
    print(f"Params: {param_list}")

    with DBContextManager(current_app.config['db_config']) as cursor:
        if cursor is None:
            print("Курсор не создан")
            raise ValueError('Не удалось подключиться')
        else:
            cursor.execute(_sql, param_list)
            return True


def call_procedure(proc_name: str, param_list: list) -> list:
    print(f"Call procedure: {proc_name}")
    print(f"Params: {param_list}")

    with DBContextManager(current_app.config['db_config']) as cursor:
        if cursor is None:
            print("Курсор не создан")
            raise ValueError('Не удалось подключиться')
        else:
            cursor.callproc(proc_name, param_list)
            rows = cursor.fetchall()

            # Получаем описание столбцов
            description = cursor.description
            if description:
                column_names = [col[0] for col in description]
            else:
                column_names = []

            # Преобразуем в список словарей
            result = []
            for row in rows:
                row_dict = {}
                for i, col_name in enumerate(column_names):
                    if i < len(row):
                        row_dict[col_name] = row[i]
                result.append(row_dict)

            print(f"Procedure result: {result}")
            return result