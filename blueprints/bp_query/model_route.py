from dataclasses import dataclass
from cursach2.database.select import select_dict

@dataclass
class ResultInfo:
    result: tuple
    status: bool
    err_message: str

#def model_route(provider, sql_file: str, user_input: dict):
 #   err_message = ''
  #  _sql = provider.get(sql_file)
   # result = select_dict(_sql, user_input)

    #if result:
     #   return ResultInfo(result=result, status=True, err_message=err_message)
    #else:
     #   err_message = 'Данные не получены'
      #  return ResultInfo(result=result, status=False, err_message=err_message)

def model_route(provider, sql_file: str, user_input: dict):
        err_message = ''
        _sql = provider.get(sql_file)
        print(f"=== DEBUG: Executing SQL ===")
        print(f"SQL file: {sql_file}")
        print(f"SQL query: {_sql}")
        print(f"User input: {user_input}")

        result = select_dict(_sql, user_input)
        print(f"Query result: {result}")
        print(f"Result length: {len(result) if result else 0}")

        if result:
            return ResultInfo(result=result, status=True, err_message=err_message)
        else:
            err_message = 'No data received from database'
            return ResultInfo(result=result, status=False, err_message=err_message)