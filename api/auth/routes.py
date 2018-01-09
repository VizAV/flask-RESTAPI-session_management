from flask import Blueprint, g, request, abort
from .control import AuthControl
from api.exceptions import AccountExists, InvalidEmail, NoAccount, InvalidCredentials, UserNotVerified
from flask import jsonify


auth_module = Blueprint('auth', __name__, url_prefix='/auth')
@auth_module.route('/signin', methods=['POST'])
def signin():
    email = request.json.get('email')
    password = request.json.get('password')
    auth = AuthControl(g.db)
    try:
        response = auth.signin(email, password)
    except NoAccount as e:
        return jsonify({'message': e.__str__()}), 404
    except (InvalidCredentials, UserNotVerified) as e:
        return jsonify({'message': e.__str__()}), 401
    except Exception as e:
        return jsonify({'message': e.__str__()}), 500
    return jsonify(response), 200

@auth_module.route('/signup', methods=['POST'])
def signup():
    email = request.json.get('email')
    password = request.json.get('password')
    if email is None or password is None:
        abort(400)
    auth = AuthControl(g.db)
    try:
        response = auth.signup(email, password)
    except InvalidEmail as e:
        return jsonify({'message': e.__str__()}), 400
    except AccountExists as e:
        return jsonify({'message': e.__str__()}), 409
    except Exception as e:
        return jsonify({'message': e.__str__()}), 500
    return jsonify(response), 200

@auth_module.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    auth = AuthControl(g.db)
    try:
        response = auth.verify_email(token)
        return response
    except Exception as e:
        return jsonify({'message': e.__str__()}), 400

@auth_module.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json.get('email')
    if email is None:
        abort(400)
    auth = AuthControl(g.db)
    try:
        response = auth.forgot_password(email)
    except Exception as e:
        return jsonify({'message': e.__str__()}), 500
    return jsonify(response), 200

@auth_module.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    password = request.json.get('password')
    if password is None:
        abort(400)
    auth = AuthControl(g.db)
    try:
        response = auth.reset_password(token, password)
    except Exception as e:
        return jsonify({'message': e.__str__()}), 500
    return jsonify(response), 200