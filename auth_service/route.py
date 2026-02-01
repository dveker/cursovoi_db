import os

from base64 import b64encode
from flask import current_app, jsonify, request, Flask

from auth_service.database.select import select_dict
from database.sql_provider import SQLProvider

app = Flask(__name__)
app.secret_key = 'You will never guess'

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


def valid_authorization_request(api_request):
    auth_header = api_request.headers.get('Authorization', '')
    if not auth_header:
        return False
    if not auth_header.startswith('Basic '):
        return False
    if len(auth_header) <= len('Basic '):
        return False
    return True


def decode_basic_authorization(api_request):
    auth_header = api_request.headers.get('Authorization')
    token = auth_header.split()[-1]
    login_and_password = b64encode(token.encode('ascii')).decode('ascii').split(':')
    if len(login_and_password) != 2:
        raise ValueError('Invalid login and password format')
    return login_and_password


@app.route('/find_user', methods=['GET'])
def find_user():
    if not valid_authorization_request(request):
        return jsonify({'status': 400, 'message': 'Bad request'})

    try:
        login_and_password = decode_basic_authorization(request)
    except Exception as e:
        return jsonify({'status': 400, 'message': f'Bad request. {str(e)}'})
    else:
        sql = provider.get('external_user.sql')
        user = select_dict(current_app.config['db_config'], sql, login_and_password)
        if not user:
            return jsonify({'status': 404, 'message': f'User not found'})
        return jsonify({'status': 200, 'message': 'OK', 'user': user[0]})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=True)