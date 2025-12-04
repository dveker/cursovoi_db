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

        ports = select_dict(provider.get('ports.sql'), {})
        ship_types = select_dict(provider.get('ship_types.sql'), {})
        teams = select_dict(provider.get('available_teams.sql'), {})


        registration_cart = session.get('registration_cart', {})

        return render_template('registration_form.html',
                               ports=ports,
                               ship_types=ship_types,
                               teams=teams,
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

        ship_name = request.form['ship_name']
        ship_type_id = request.form['ship_type_id']
        tonnage = float(request.form['tonnage'])
        home_port = request.form['home_port']
        team_id = request.form['team_id']


        if not team_id:
            flash('Выберите бригаду для разгрузки!', 'error')
            return redirect(url_for('bp_registration.registration_index'))


        team_exists = select_dict(provider.get('check_team_exists.sql'),
                                  {'team_id': team_id})

        if not team_exists:
            flash('Выбранная бригада не существует!', 'error')
            return redirect(url_for('bp_registration.registration_index'))


        team_free = select_dict(provider.get('check_team_free.sql'),
                                {'team_id': team_id})

        if not team_free:
            flash('Выбранная бригада уже занята!', 'error')
            return redirect(url_for('bp_registration.registration_index'))


        for item_id, ship_data in session['registration_cart'].items():
            if (ship_data['ship_name'] == ship_name and
                    ship_data['home_port'] == home_port):
                flash(f'Корабль "{ship_name}" из порта {home_port} уже в корзине!', 'warning')
                return redirect(url_for('bp_registration.registration_index'))


        cart_item_id = f"ship_{len(session['registration_cart'])}"


        session['registration_cart'][cart_item_id] = {
            'ship_name': ship_name,
            'ship_type_id': ship_type_id,
            'tonnage': tonnage,
            'home_port': home_port,
            'team_id': team_id
        }

        session.modified = True
        flash(f'Корабль "{ship_name}" добавлен в корзину!', 'success')
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

            if not ship_data.get('team_id'):
                flash(f'У корабля "{ship_data["ship_name"]}" не назначена бригада!', 'error')
                continue


            register_result = execute_sql(provider.get('register_ship.sql'), {
                'name': ship_data['ship_name'],
                'ship_type_id': ship_data['ship_type_id'],
                'tonnage': ship_data['tonnage'],
                'home_port': ship_data['home_port']
            })

            if register_result:
                ships_registered += 1





                try:

                    ship_id_result = select_dict(provider.get('get_last_ship_id.sql'),
                                                 {'name': ship_data['ship_name'], 'home_port': ship_data['home_port']})

                    if ship_id_result:
                        ship_id = ship_id_result[0]['id']
                        execute_sql(provider.get('register_arrival.sql'), [ship_id])
                        reg_id_result = select_dict(provider.get('get_last_registration_id.sql'),
                                                    {'ship_id': ship_id})
                        if reg_id_result:
                            registration_id = reg_id_result[0]['id']


                            execute_sql(provider.get('assign_team.sql'),
                                        [registration_id, ship_data['team_id']])

                            flash(f'Для корабля "{ship_data["ship_name"]}" назначена бригада!', 'info')
                except Exception as team_error:
                    print(f"Error assigning team: {team_error}")
                    flash(f'Не удалось назначить бригаду для "{ship_data["ship_name"]}"', 'warning')

        session.pop('registration_cart', None)
        session.modified = True

        return render_template('registration_success.html',
                               ships_count=ships_registered)

    except Exception as e:
        print(f"Error submitting registration: {e}")
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
        print(f"=== DEBUG: Completing unloading for registration {registration_id} ===")

        try:
            complete_sql = provider.get('complete_ship_departure.sql')
            print(f"complete_ship_departure.sql: {complete_sql}")
        except Exception as e:
            print(f"Error reading complete_ship_departure.sql: {e}")
            complete_sql = "UPDATE ship_registrations SET departure_date = NOW() WHERE id = %s"

        try:
            free_sql = provider.get('free_team.sql')
            print(f"free_team.sql: {free_sql}")
        except Exception as e:
            print(f"Error reading free_team.sql: {e}")
            free_sql = "UPDATE unloading_teams SET ship_registration_id = NULL WHERE ship_registration_id = %s"


        print(f"Executing departure update: {complete_sql} with param: {registration_id}")
        execute_sql(complete_sql, [registration_id])


        print(f"Executing team free: {free_sql} with param: {registration_id}")
        execute_sql(free_sql, [registration_id])

        flash('Разгрузка завершена! Бригада освобождена.', 'success')
        return redirect(url_for('bp_registration.active_ships'))

    except Exception as e:
        print(f"Error completing unloading: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('bp_registration.active_ships'))