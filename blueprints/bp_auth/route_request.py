from dataclasses import dataclass
from cursach2.database.select import select_dict

@dataclass
class ResultInfo:
    result: tuple
    status: bool
    err_message: str

def model_route(provider, sql_file: str, user_input: dict):
    err_message = ''
    print("=== DEBUG MODEL_ROUTE ===")
    print(f"User input: {user_input}")

    _sql = provider.get(sql_file)
    print(f"SQL query: {_sql}")

    result = select_dict(_sql, user_input)
    print(f"Query result: {result}")
    print(f"Result type: {type(result)}")

    if result:
        print(" Данные получены успешно")
        return ResultInfo(result=result, status=True, err_message=err_message)
    else:
        err_message = 'Данные не получены'
        print(f" {err_message}")
        return ResultInfo(result=result, status=False, err_message=err_message)