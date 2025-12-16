from functools import wraps
from flask import session, redirect, url_for, render_template
import json
import os


def load_access_config():

    try:

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'data', 'db_access.json')

        if os.path.exists(config_path):
            with open(config_path) as f:
                return json.load(f)
        else:
            # Если файл не найден, возвращаем пустой словарь
            return {}

    except json.JSONDecodeError as e:
        print(f"Error parsing db_access.json: {e}")
        return {}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth_bp.auth_index'))
        return f(*args, **kwargs)

    return decorated_function


def group_required(allowed_groups):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in'):
                return redirect(url_for('auth_bp.auth_index'))

            user_group = session.get('user_group')
            if user_group not in allowed_groups:
                return render_template('access_denied.html')

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Создаем декораторы для конкретных групп
admin_required = group_required(['admin'])
manager_required = group_required(['manager', 'admin'])
user_required = group_required(['user', 'manager', 'admin'])