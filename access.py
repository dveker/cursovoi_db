# access.py
from functools import wraps
from flask import session, redirect, url_for, render_template

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth_bp.auth_index'))  # Исправлено здесь
        return f(*args, **kwargs)
    return decorated_function

def group_required(allowed_groups):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in'):
                return redirect(url_for('auth_bp.auth_index'))  # И здесь
            user_group = session.get('user_group')
            if user_group not in allowed_groups:
                return render_template('access_denied.html')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


admin_required = group_required(['admin'])
manager_required = group_required(['manager', 'admin'])
user_required = group_required(['user', 'manager', 'admin'])
registration_required = group_required(['admin', 'manager'])