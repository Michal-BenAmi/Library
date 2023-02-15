from flask import request, make_response, jsonify, g

from app.api.library_db_schema import User, Checkout
from functools import wraps


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        username = request.authorization.username
        user = User.query.filter_by(username=username).first()
        is_admin = user.is_admin
        if not is_admin:
            return make_response(jsonify({'message': 'Unauthorized access. Admin rights required.'}), 401)
        return f(*args, **kwargs)
    return decorated


def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None


def authenticate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        g.user = user.id
        if 'user_id' in kwargs and g.user != kwargs['user_id']:
            return jsonify({'message': 'Unauthorized access. Different user.'}), 401
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    auth = request.authorization
    if not auth or not authenticate_user(auth.username, auth.password):
        return jsonify({'message': 'Unauthorized access'}), 401
    user = User.query.filter_by(username=auth.username).first()
    g.user = user.id
    return user


def get_user_book_count(user_id):
    checkout_count = Checkout.query.filter_by(user_id=user_id).count()
    return checkout_count
