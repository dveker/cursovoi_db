import os
from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from cursach2.database.sql_provider import SQLProvider
from cursach2.database.select import select_dict, execute_sql
from cursach2.access import login_required, group_required

blueprint_registration = Blueprint('bp_registration', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_registration.route('/', methods=['GET'])
@login_required
@group_required(['admin', 'manager'])
def registration_index():
    try:
        # Загружаем данные для формы напрямую по имени файла
        ports = select_dict(provider.get('ports.sql'), {})
        ship_types = select_dict(provider.get('ship_types.sql'), {})
        teams = select_dict(provider.get('available_teams.sql'), {})
        berths = select_dict(provider.get('available_berths.sql'), {})
        berth_types = select_dict(provider.get('berth_types.sql'), {})

        # Получаем корзину из сессии
        registration_cart = session.get('registration_cart', {})

        return render_template('registration_form.html',
                               ports=ports,
                               ship_types=ship_types,
                               teams=teams,
                               berths=berths,
                               berth_types=berth_types,
                               cart=registration_cart)

    except Exception as e:
        print(f"Error in registration_index: {str(e)}")
        flash(f'Ошибка загрузки данных: {str(e)}', 'error')
        return render_template('registration_error.html',
                               error=f'Ошибка загрузки данных: {str(e)}')


@blueprint_registration.route('/add', methods=['POST'])
@login_required
@group_required(['admin', 'manager'])
def add_to_registration():
    if 'registration_cart' not in session:
        session['registration_cart'] = {}

    try:
        # Получаем данные из формы
        ship_name = request.form['ship_name']
        ship_type_id = request.form['ship_type_id']
        tonnage = float(request.form['tonnage'])
        home_port = request.form['home_port']
        team_id = request.form['team_id']
        berth_id = request.form.get('berth_id')

        # Проверяем обязательные поля
        if not ship_name or not ship_type_id or not tonnage or not home_port:
            flash('Заполните все обязательные поля!', 'error')
            return redirect(url_for('bp_registration.registration_index'))

        if not team_id:
            flash('Выберите бригаду для разгрузки!', 'error')
            return redirect(url_for('bp_registration.registration_index'))

        # Проверяем существование бригады
        team_exists = select_dict(provider.get('check_team_exists.sql'),
                                  [team_id])

        if not team_exists:
            flash('Выбранная бригада не существует!', 'error')
            return redirect(url_for('bp_registration.registration_index'))

        # Проверяем доступность бригады
        team_available = select_dict(provider.get('check_team_available.sql'),
                                     {'team_id': team_id})

        if not team_available:
            flash('Выбранная бригада уже занята!', 'error')
            return redirect(url_for('bp_registration.registration_index'))

        # Проверяем доступность причала, если выбран
        if berth_id:
            berth_available = select_dict(provider.get('check_berth_available.sql'),
                                          {'berth_id': berth_id})
            if not berth_available:
                flash('Выбранный причал уже занят!', 'error')
                return redirect(url_for('bp_registration.registration_index'))

        # Проверяем дублирование в корзине
        for item_id, ship_data in session['registration_cart'].items():
            if (ship_data['ship_name'] == ship_name and
                    ship_data['home_port'] == home_port):
                flash(f'Корабль "{ship_name}" из порта {home_port} уже в корзине!', 'warning')
                return redirect(url_for('bp_registration.registration_index'))

        # Создаем уникальный ID для элемента корзины
        cart_item_id = f"ship_{len(session['registration_cart'])}"

        # Добавляем в корзину
        session['registration_cart'][cart_item_id] = {
            'ship_name': ship_name,
            'ship_type_id': ship_type_id,
            'tonnage': tonnage,
            'home_port': home_port,
            'team_id': team_id,
            'berth_id': berth_id
        }
        session.modified = True

        flash(f'Корабль "{ship_name}" добавлен в корзину!', 'success')
        return redirect(url_for('bp_registration.registration_index'))

    except ValueError as e:
        flash('Некорректное значение водоизмещения!', 'error')
        return redirect(url_for('bp_registration.registration_index'))
    except KeyError as e:
        flash(f'Не все поля формы заполнены! Отсутствует: {str(e)}', 'error')
        return redirect(url_for('bp_registration.registration_index'))
    except Exception as e:
        print(f"Error adding to registration: {e}")
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('bp_registration.registration_index'))


@blueprint_registration.route('/remove/<cart_item_id>', methods=['POST'])
@login_required
@group_required(['admin', 'manager'])
def remove_from_registration(cart_item_id):
    if 'registration_cart' in session and cart_item_id in session['registration_cart']:
        ship_name = session['registration_cart'][cart_item_id]['ship_name']
        del session['registration_cart'][cart_item_id]
        session.modified = True
        flash(f'Корабль "{ship_name}" удален из корзины!', 'info')

    return redirect(url_for('bp_registration.registration_index'))


@blueprint_registration.route('/clear', methods=['POST'])
@login_required
@group_required(['admin', 'manager'])
def clear_registration():
    session.pop('registration_cart', None)
    flash('Корзина регистрации очищена!', 'info')
    return redirect(url_for('bp_registration.registration_index'))


@blueprint_registration.route('/submit', methods=['POST'])
@login_required
@group_required(['admin', 'manager'])
def submit_registration():
    registration_cart = session.get('registration_cart', {})

    if not registration_cart:
        flash('Корзина регистрации пуста!', 'warning')
        return redirect(url_for('bp_registration.registration_index'))

    try:
        ships_registered = 0

        for cart_item_id, ship_data in registration_cart.items():
            # Проверяем наличие бригады
            if not ship_data.get('team_id'):
                flash(f'У корабля "{ship_data["ship_name"]}" не назначена бригада!', 'error')
                continue

            try:
                # 1. Регистрируем корабль
                execute_sql(provider.get('register_ship.sql'), {
                    'name': ship_data['ship_name'],
                    'ship_type_id': ship_data['ship_type_id'],
                    'tonnage': ship_data['tonnage'],
                    'home_port': ship_data['home_port']
                })

                # 2. Получаем ID зарегистрированного корабля
                ship_id_result = select_dict(provider.get('get_last_ship_id.sql'), [
                    ship_data['ship_name'],
                    ship_data['home_port']
                ])

                if not ship_id_result:
                    flash(f'Не удалось получить ID корабля "{ship_data["ship_name"]}"', 'warning')
                    continue

                ship_id = ship_id_result[0]['id']

                # 3. Регистрируем прибытие корабля
                if ship_data.get('berth_id'):
                    # С причалом
                    execute_sql(provider.get('register_arrival_with_berth.sql'), {
                        'ship_id': ship_id,
                        'berth_id': ship_data['berth_id']
                    })
                else:
                    # Без причала
                    execute_sql(provider.get('register_arrival.sql'), [
                        ship_id
                    ])

                # 4. Получаем ID регистрации прибытия
                reg_id_result = select_dict(provider.get('get_last_registration_id.sql'), [
                    ship_id
                ])

                if not reg_id_result:
                    flash(f'Не удалось получить ID регистрации для корабля "{ship_data["ship_name"]}"', 'warning')
                    continue

                registration_id = reg_id_result[0]['id']

                # 5. Назначаем бригаду
                execute_sql(provider.get('assign_team_to_ship.sql'), [
                    registration_id,
                    ship_data['team_id']
                ])

                ships_registered += 1
                flash(f'Корабль "{ship_data["ship_name"]}" успешно зарегистрирован!', 'success')

            except Exception as ship_error:
                print(f"Error registering ship {ship_data['ship_name']}: {ship_error}")
                flash(f'Ошибка при регистрации корабля "{ship_data["ship_name"]}": {str(ship_error)}', 'error')
                continue

        # Очищаем корзину после успешной регистрации
        session.pop('registration_cart', None)
        session.modified = True

        return render_template('registration_success.html',
                               ships_count=ships_registered,
                               total_ships=len(registration_cart))

    except Exception as e:
        print(f"Error submitting registration: {e}")
        import traceback
        traceback.print_exc()
        return render_template('registration_error.html',
                               error=f'Ошибка регистрации: {str(e)}')


@blueprint_registration.route('/active', methods=['GET'])
@login_required
@group_required(['admin', 'manager'])
def active_ships():
    try:
        active_ships = select_dict(provider.get('active_ships_with_teams.sql'), {})

        return render_template('active_ships.html',
                               active_ships=active_ships or [])

    except Exception as e:
        print(f"Error loading active ships: {e}")
        flash(f'Ошибка загрузки данных: {str(e)}', 'error')
        return redirect(url_for('bp_registration.registration_index'))


@blueprint_registration.route('/complete/<int:registration_id>', methods=['POST'])
@login_required
@group_required(['admin', 'manager'])
def complete_unloading(registration_id):
    try:
        # Завершение разгрузки
        execute_sql(provider.get('complete_unloading.sql'), {
            'registration_id': registration_id
        })

        flash('Разгрузка завершена! Бригада освобождена.', 'success')
        return redirect(url_for('bp_registration.active_ships'))

    except Exception as e:
        print(f"Error completing unloading: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Ошибка при завершении разгрузки: {str(e)}', 'error')
        return redirect(url_for('bp_registration.active_ships'))


# История кораблей
@blueprint_registration.route('/history', methods=['GET'])
@login_required
@group_required(['admin', 'manager'])
def ship_history():
    try:
        # Получаем историю всех кораблей
        history = select_dict(provider.get('ship_history.sql'), {})

        return render_template('ship_history.html',
                               ship_history=history or [])

    except Exception as e:
        print(f"Error loading ship history: {e}")
        flash(f'Ошибка загрузки истории: {str(e)}', 'error')
        return redirect(url_for('bp_registration.registration_index'))


# Детали корабля
@blueprint_registration.route('/ship/<int:ship_id>', methods=['GET'])
@login_required
@group_required(['admin', 'manager'])
def ship_details(ship_id):
    try:
        # Получаем информацию о корабле
        ship_info = select_dict(provider.get('ship_details.sql'), {'ship_id': ship_id})

        # Получаем историю рейсов корабля
        ship_trips = select_dict(provider.get('ship_trips_history.sql'), {'ship_id': ship_id})

        return render_template('ship_details.html',
                               ship_info=ship_info[0] if ship_info else {},
                               ship_trips=ship_trips or [])

    except Exception as e:
        print(f"Error loading ship details: {e}")
        flash(f'Ошибка загрузки информации о корабле: {str(e)}', 'error')
        return redirect(url_for('bp_registration.registration_index'))