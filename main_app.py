import os
import json
from flask import Flask, render_template, redirect, url_for, session
from blueprints.bp_auth.auth import auth_bp
from blueprints.bp_query.query import blueprint_query
from blueprints.bp_report.report import blueprint_report
from blueprints.bp_registration.registration import blueprint_registration

from access import login_required, load_access_config

app = Flask(__name__)
app.secret_key = 'your-very-secret-key-12345'

# Загрузка конфигураций
base_dir = os.path.dirname(os.path.abspath(__file__))

# Конфигурация БД
db_config_path = os.path.join(base_dir, 'data', 'db_config.json')
with open(db_config_path) as f:
    app.config['db_config'] = json.load(f)

# Регистрация blueprint'ов
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(blueprint_query, url_prefix='/query')
app.register_blueprint(blueprint_report, url_prefix='/reports')
app.register_blueprint(blueprint_registration, url_prefix='/registration')


@app.context_processor
def inject_user():
    def has_access(allowed_groups):
        """Проверяет доступ для текущего пользователя к группам"""
        user_group = session.get('user_group')
        return user_group in allowed_groups if user_group else False

    def is_admin():
        """Проверяет, является ли пользователь админом"""
        return session.get('user_group') == 'admin'

    def is_manager():
        """Проверяет, является ли пользователь менеджером или админом"""
        user_group = session.get('user_group')
        return user_group in ['admin', 'manager']

    def get_user_blueprints():
        """Возвращает список blueprint'ов доступных пользователю (для отладки)"""
        user_group = session.get('user_group')
        if not user_group:
            return []

        # Загружаем конфигурацию
        access_config = load_access_config()
        return access_config.get(user_group, [])

    return dict(
        session=session,
        has_access=has_access,
        is_admin=is_admin,
        is_manager=is_manager,
        get_user_blueprints=get_user_blueprints
    )


@app.route('/main', methods=['GET'])
@login_required
def main_menu():
    # Для отладки: печатаем доступные blueprint'ы
    user_group = session.get('user_group')
    if user_group:
        access_config = load_access_config()
        print(f"User {session.get('user_id')} ({user_group}) has access to: {access_config.get(user_group, [])}")

    return render_template('menu.html')


@app.route('/exit', methods=['GET'])
@login_required
def menu_exit():
    session.clear()
    return redirect(url_for('auth_bp.auth_index'))


@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('main_menu'))
    return render_template('main.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)