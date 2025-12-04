import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from flask import Blueprint, render_template, session, request, redirect, url_for, current_app
from cursach2.database.DBcm import DBContextManager

auth_bp = Blueprint('auth_bp', __name__, template_folder='templates')

@auth_bp.route('/', methods=['GET', 'POST'])
def auth_index():
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        print(f"=== DEBUG AUTH ===")
        print(f"Login attempt: {username}")

        # Используем прямой SQL запрос
        sql_query = "SELECT id, user_group FROM users WHERE username = %s AND password = %s"

        try:
            with DBContextManager(current_app.config['db_config']) as cursor:
                if cursor is None:
                    return "Ошибка подключения к БД", 500

                cursor.execute(sql_query, [username, password])
                user_data = cursor.fetchone()

                print(f"Database result: {user_data}")

                if user_data:
                    session['user_id'] = user_data[0]
                    session['user_group'] = user_data[1]
                    session['logged_in'] = True

                    print(f"Session SET: user_id='{user_data[0]}', user_group='{user_data[1]}'")
                    return redirect(url_for('main_menu'))
                else:
                    print(f"No user found or wrong password")
                    return render_template('login.html', error='Неверное имя пользователя или пароль')

        except Exception as e:
            print(f"Database error: {e}")
            return render_template('login.html', error='Ошибка базы данных')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_bp.auth_index'))