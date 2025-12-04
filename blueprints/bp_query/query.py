
import os
import sys
import decimal

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from flask import Blueprint, render_template, request, session, current_app
from cursach2.database.sql_provider import SQLProvider
from .model_route import model_route
from cursach2.access import login_required, admin_required

blueprint_query = Blueprint('blueprint_query', __name__, template_folder='templates')


@blueprint_query.route('/query', methods=['GET', 'POST'])
@login_required
@admin_required
def query_index():
    if request.method == 'GET':
        return render_template('dynamic.html')

    else:
        user_input = {}

        # Базовые поисковые запросы
        if 'employee_name' in request.form:
            employee_name = f"%{request.form.get('employee_name')}%"
            user_input['name1'] = employee_name
            user_input['name2'] = employee_name
            sql_file = 'employees_by_name.sql'
        elif 'ship_name' in request.form:
            user_input['ship_name'] = f"%{request.form.get('ship_name')}%"
            sql_file = 'ships_by_name.sql'
        elif 'berth_type' in request.form:
            user_input['berth_type'] = request.form.get('berth_type')
            sql_file = 'berths_by_type.sql'

        # Интерактивный запрос с вводом типа корабля
        elif 'ship_type_input' in request.form:
            user_input['ship_type'] = request.form.get('ship_type_input')
            sql_file = 'ship_turnover_by_type.sql'
        else:
            return render_template('dynamic.html', error='Неизвестный тип запроса')

        sql_path = os.path.join(os.path.dirname(__file__), 'sql')
        provider = SQLProvider(sql_path)

        if sql_file not in provider.scripts:
            return render_template('dynamic.html', error=f'SQL файл {sql_file} не найден')

        result_info = model_route(provider, sql_file, user_input)

        if result_info.status:
            if result_info.result:
                # Определяем колонки для разных типов запросов
                columns_mapping = {
                    'employees_by_name.sql': ['id', 'first_name', 'last_name', 'profession', 'hire_date'],
                    'ships_by_name.sql': ['id', 'name', 'type_name', 'tonnage', 'home_port'],
                    'berths_by_type.sql': ['id', 'type_name', 'length', 'depth'],
                    'ship_turnover_by_type.sql': ['ship_type', 'total_ships_of_type', 'total_visits', 'avg_tonnage',
                                                  'avg_stay_hours', 'current_in_port', 'first_visit', 'last_visit']
                }

                columns = columns_mapping.get(sql_file, [f'col_{i}' for i in range(len(result_info.result[0]))])

                result_dicts = []
                for row in result_info.result:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        if i < len(row):
                            value = row[col] if isinstance(row, dict) else row[i]
                            # Преобразуем Decimal в float для корректного форматирования
                            if isinstance(value, decimal.Decimal):
                                value = float(value)
                            row_dict[col] = value
                    result_dicts.append(row_dict)

                return render_template('dynamic.html', result=result_dicts, query_type=sql_file)
            else:
                return render_template('dynamic.html', error='Данные не найдены')
        else:
            return render_template('dynamic.html', error=result_info.err_message)
