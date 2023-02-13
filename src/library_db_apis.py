import re

from flask import request, make_response, jsonify, g

from src.library_db_schema import *
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


# API to register a new user
@app.route('/api/register', methods=['POST'])
def register():
    if 'username' not in request.json:
        return make_response(({'error': 'Missing required parameter: username'}), 400)
    if 'email' not in request.json:
        return make_response(({'error': 'Missing required parameter: email'}), 400)
    if 'password' not in request.json:
        return make_response(({'error': 'Missing required parameter: password'}), 400)

    username = request.json['username'].strip()
    email = request.json['email'].strip()
    password = request.json['password'].strip()
    is_admin = request.json.get('is_admin', False)

    # validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return make_response(({'error': 'Invalid email format'}), 400)

    user = User(username=username, email=email, password=password, is_admin=is_admin)

    try:
        db.session.add(user)
        db.session.commit()
        return make_response(({'message': 'User created successfully'}), 201)
    except:
        return make_response(({'error': 'Error creating user'}), 500)


# API to remove a registered user
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@auth.login_required
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return make_response("User not found", 404)

    try:
        db.session.delete(user)
        db.session.commit()
        return make_response("user deleted", 204)
    except:
        return make_response("Error removing user", 500)


# API to get all books in the catalog. filter by author/title/is_available
@app.route('/api/books', methods=['GET'])
def get_books():
    author = request.args.get('author', '').strip()
    title = request.args.get('title', '').strip()
    is_available = request.args.get('is_available', default=None, type=bool)

    query = Book.query

    if author:
        query = query.filter_by(author=author)
    if title:
        query = query.filter_by(title=title)
    if is_available:
        query = query.filter_by(is_available=is_available)

    books = query.all()
    return make_response(books_schema.jsonify(books), 200)


# API to get a book details
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return make_response("Invalid book", 400)
    return make_response(book_schema.jsonify(book), 200)


# API to add a new book
@app.route('/api/books', methods=['POST'])
@auth.login_required
@admin_required
def add_book():
    title = request.json['title'].strip() if request.json['title'] else None
    author = request.json['author'].strip() if request.json['author'] else None

    if not title:
        return make_response("Invalid book title", 400)
    if not author:
        return make_response("Invalid book author", 400)
    book = Book(title=title, author=author)
    try:
        db.session.add(book)
        db.session.commit()
        return make_response(book_schema.jsonify(book), 201)
    except:
        return make_response("Error adding book", 500)


# API to remove a book
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@auth.login_required
@admin_required
def remove_book(book_id):
    book = Book.query.get(book_id)

    try:
        db.session.delete(book)
        db.session.commit()
        return make_response(book_schema.jsonify(book), 200)
    except:
        return make_response("Error removing book", 500)


# API to checkout book for user
@app.route('/api/checkout', methods=['POST'])
@auth.login_required
def checkout_book():
    user = get_current_user()

    # user id can be part of the request or from th auth token user
    user_id = request.json.get('user_id', user.id)
    book_id = request.json['book_id']

    if not book_id:
        return make_response("Missing parameter book in the request", 400)

    book = Book.query.get(book_id)

    if not user or not book:
        return make_response("Invalid user or book", 400)

    if get_user_book_count(user_id) >= 10:
        return make_response("User has already checked out the maximum number of books (10)", 500)

    if not book.is_available:
        return make_response("Book is not available for checkout", 500)

    checked = Checkout(book_id=book_id, user_id=user_id)
    book = Book.query.get(book_id)
    try:
        book.is_available = False
        db.session.add(checked)
        db.session.commit()

        return jsonify({"id": checked.id, "user_id": user_id, "book_id": book_id, "checkout_date": checked.checkout_date}), 201
    except:
        return make_response("Error checking out book", 500)


# API to return a book from user
@app.route('/api/checkouts/<int:book_id>', methods=['PUT'])
@auth.login_required
def return_book(book_id):
    if not book_id:
        return make_response("Missing parameter book in the request", 400)
    book = Book.query.get(book_id)
    if not book:
        return make_response("Invalid book", 400)

    try:
        checkout = Checkout.query.get(book_id)
        db.session.delete(checkout)
        db.session.commit()
        book.is_available = True
        return make_response(book_schema.jsonify(book), 200)
    except:
        return make_response("Error returning book", 500)


# API to get all the checkouts
@app.route('/api/checkouts', methods=['GET'])
@auth.login_required
@admin_required
def get_checkouts():
    checkouts = Checkout.query.all()
    result = []
    for checkout in checkouts:
        user = User.query.get(checkout.user_id)
        result.append({
            'checkout_id': checkout.id,
            'book_id': checkout.book_id,
            'user_id': checkout.user_id,
            'user_name': user.username,
            'checkout_date': checkout.checkout_date
        })
    return make_response(jsonify({'checkouts': result}), 200)


# API to get all the checkouts for user
@app.route('/api/checkouts/me', methods=['GET'])
@auth.login_required
@authenticate
def get_checkouts_by_user():
    try:
        user = get_current_user()
        user_id = user.id
        checkouts = Checkout.query.filter_by(user_id=user_id).all()
        if not checkouts:
            return make_response("No checkouts found for the user id provided", 404)
        # user = User.query.get(user_id)
        result = []
        for checkout in checkouts:
            result.append({
                'checkout_id': checkout.id,
                'book_id': checkout.book_id,
                'user_id': checkout.user_id,
                'user_name': user.username,
                'checkout_date': checkout.checkout_date
            })
        return jsonify({'checkouts': result}), 200
    except:
        return make_response("Error get_checkouts_by_user", 500)


def get_user_fines(user_id):
    if not user_id:
        return make_response("Missing parameter user_id", 400)
    user = User.query.get(user_id)
    if not user:
        make_response("Invalid user", 400)

    checkouts = Checkout.query.filter_by(user_id=user_id)
    fine_amount = 0

    for checkout in checkouts:
        days_overdue = (datetime.now() - checkout.checkout_date).days - 14
        if days_overdue > 0:
            fine_amount += days_overdue * 0.10

    return make_response(jsonify({"user_id": user_id, "fine_amount": fine_amount}), 200)


# API to allow a user to view if they owe a fine and how much it is
@app.route('/api/fines/<int:user_id>', methods=['GET'])
@auth.login_required
def get_user_id_fines(user_id):
    return get_user_fines(user_id)


# API to allow a user to view if they owe a fine and how much it is
@app.route('/api/fines/me', methods=['GET'])
@auth.login_required
def get_my_fines():
    user = get_current_user()
    return get_user_fines(user.id)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


