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


def select_dict(_sql: str, params=None) -> list:
    if params is None:
        params = {}

    print(f"SQL: {_sql}")
    print(f"Params: {params}")
    print(f"Params type: {type(params)}")

    try:
        with DBContextManager(current_app.config['db_config']) as cursor:
            if cursor is None:
                print("Курсор не создан")
                raise ValueError('Не удалось подключиться')

            # АВТОМАТИЧЕСКОЕ ПРЕОБРАЗОВАНИЕ ПАРАМЕТРОВ
            # Если SQL содержит %s и передали словарь - преобразуем в список
            if '%s' in _sql and isinstance(params, dict):
                print(f"⚠️ SQL использует %s, но params - словарь. Преобразую в список...")
                params = list(params.values())
                print(f"Преобразованные params: {params}")
            elif '%(' in _sql and isinstance(params, list):
                print(f"⚠️ SQL использует %(name)s, но params - список. Оставляем как есть...")
                # В этом случае нужно оставить как есть, будет ошибка при выполнении
                # Это поможет отладить проблему

            # Выполняем запрос
            if params:
                cursor.execute(_sql, params)
            else:
                cursor.execute(_sql)

            # Получаем описание столбцов
            description = cursor.description
            if description:
                column_names = [col[0] for col in description]
            else:
                column_names = []

            # Получаем данные
            rows = cursor.fetchall()

            # Преобразуем в список словарей
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
        print(f" Error in select_dict: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []


def execute_sql(_sql: str, param_list: list) -> bool:
    print(f"Execute SQL: {_sql}")
    print(f"Params: {param_list}")
    print(f"Params type: {type(param_list)}")

    try:
        with DBContextManager(current_app.config['db_config']) as cursor:
            if cursor is None:
                print("Курсор не создан")
                raise ValueError('Не удалось подключиться')
            else:
                # Аналогичное преобразование для execute_sql
                if '%s' in _sql and isinstance(param_list, dict):
                    print(f"⚠️ SQL использует %s, но param_list - словарь. Преобразую в список...")
                    param_list = list(param_list.values())
                    print(f"Преобразованный param_list: {param_list}")

                cursor.execute(_sql, param_list)
                return True
    except Exception as e:
        print(f" Error in execute_sql: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def call_procedure(proc_name: str, param_list: list) -> list:
    print(f"Call procedure: {proc_name}")
    print(f"Params: {param_list}")

    try:
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
    except Exception as e:
        print(f" Error in call_procedure: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []