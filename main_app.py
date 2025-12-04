import os
import json
from flask import Flask, render_template, redirect, url_for, session
from blueprints.bp_auth.auth import auth_bp
from blueprints.bp_query.query import blueprint_query
from blueprints.bp_report.report import blueprint_report
from blueprints.bp_registration.registration import blueprint_registration

from access import login_required

app = Flask(__name__)
app.secret_key = 'your-very-secret-key-12345'


base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, 'data', 'db_config.json')
with open(config_path) as f:
    app.config['db_config'] = json.load(f)


app.config['REPORT_CREATORS'] = ['admin', 'manager']
app.config['REPORT_VIEWERS'] = ['admin', 'manager', 'user']

app.config['REGISTRATION_ACCESS'] = ['admin', 'manager']


app.config['DISPATCH_ACCESS'] = ['admin', 'manager']


app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(blueprint_query, url_prefix='/query')
app.register_blueprint(blueprint_report, url_prefix='/reports')
app.register_blueprint(blueprint_registration, url_prefix='/registration')

@app.context_processor
def inject_user():
    return dict(session=session)

@app.route('/main', methods=['GET'])
@login_required
def main_menu():
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