from dataclasses import dataclass
from cursach2.database.select import select_dict, execute_sql, call_procedure


@dataclass
class ResultInfo:
    result: tuple
    status: bool
    err_message: str


def model_route(provider, sql_file: str, user_input: dict):
    _sql = provider.get(sql_file)
    print(f"SQL: {_sql}")
    print(f"User input: {user_input}")

    try:

        if _sql.strip().upper().startswith('CALL'):
            proc_name = _sql.split(' ')[1].split('(')[0]
            user_list = [user_input[key] for key in user_input]
            result = call_procedure(proc_name, user_list)


            if 'CreateShipTypeReport' in proc_name:
                if result and len(result) > 0:
                    result_message = result[0]
                    if isinstance(result_message, tuple):
                        result_message = result_message[0]


                    if 'уже существует' in str(result_message):

                        return ResultInfo(result=(), status=False, err_message=str(result_message)) #


                return ResultInfo(result=("success",), status=True, err_message='')


            elif result:
                return ResultInfo(result=result, status=True, err_message='')
            else:
                return ResultInfo(result=[], status=False, err_message='Нет данных')


        elif _sql.upper().startswith('SELECT'):
            result = select_dict(_sql, user_input)
            if result:
                return ResultInfo(result=result, status=True, err_message='')
            else:
                return ResultInfo(result=result, status=False, err_message='Нет данных')

        else:
            user_list = [user_input[key] for key in user_input]
            execute_sql(_sql, user_list)
            return ResultInfo(result=("success",), status=True, err_message='')

    except Exception as e:
        print(f"Error in model_route: {e}")
        return ResultInfo(result=(), status=False, err_message=str(e))