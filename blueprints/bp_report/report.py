import os
from flask import Blueprint, render_template, request
from cursach.cursach.database.sql_provider import SQLProvider
from .model_route import model_route
from cursach.cursach.access import login_required, group_required

blueprint_report = Blueprint('bp_report', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_report.route('/', methods=['GET'])
@login_required
def report_menu_handle():
    return render_template('report_menu.html')


@blueprint_report.route('/create_report', methods=['GET'])
@login_required
@group_required(['admin', 'manager'])
def create_report_handle():
    return render_template('create_report.html')


@blueprint_report.route('/create_report', methods=['POST'])
@login_required
@group_required(['admin', 'manager'])
def create_report_form():
    user_input = request.form

    try:
        month = int(user_input['month'])
        year = int(user_input['year'])

        if month not in range(1, 13):
            return render_template('create_report.html', message='Неверный месяц (должен быть от 1 до 12)')
        if year < 2020 or year > 2030:
            return render_template('create_report.html', message='Неверный год (должен быть от 2020 до 2030)')

    except ValueError:
        return render_template('create_report.html', message='Неверный формат данных')

    # Создаем отчет
    sql_params = {'month': month, 'year': year}
    result_info = model_route(provider, 'create_ship_report.sql', sql_params)

    if result_info.status:
        message = f'Отчет по типам кораблей за {month}/{year} успешно создан и сохранен!'
        # Показываем созданный отчет
        result_info = model_route(provider, 'get_ship_report.sql', user_input)
        if result_info.status and result_info.result:
            reports = result_info.result
            return render_template('report_result.html',
                                   reports=reports,
                                   month=month,
                                   year=year,
                                   message=message)
    else:
        message = f'Ошибка: {result_info.err_message}'

    return render_template('create_report.html', message=message)


@blueprint_report.route('/show_reports', methods=['GET'])
@login_required
def show_reports_handle():
    return render_template('show_reports.html')


@blueprint_report.route('/show_reports', methods=['POST'])
@login_required
def show_reports_form():
    user_input = request.form

    try:
        month = int(user_input['month'])
        year = int(user_input['year'])

        if month not in range(1, 13):
            return render_template('show_reports.html', error='Неверный месяц')
        if year < 2020 or year > 2030:
            return render_template('show_reports.html', error='Неверный год')

    except ValueError:
        return render_template('show_reports.html', error='Неверный формат данных')

    # Показываем сохраненный отчет
    result_info = model_route(provider, 'get_ship_report.sql', user_input)

    if result_info.status and result_info.result:
        reports = result_info.result
        return render_template('report_result.html',
                               reports=reports,
                               month=month,
                               year=year)
    else:
        return render_template('show_reports.html', error=f'Нет сохраненного отчета за {month}/{year}')