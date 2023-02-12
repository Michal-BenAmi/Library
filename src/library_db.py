from datetime import datetime
import re, json

from flask import Flask, request, make_response
from flask_oauthlib.provider import OAuth2Provider
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://libuser:library123@localhost/library_management'
db = SQLAlchemy(app)
oauth = OAuth2Provider(app)
ma = Marshmallow(app)


# class Token(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     access_token = db.Column(db.String(255), unique=True)
#     refresh_token = db.Column(db.String(255), unique=True)
#     expires = db.Column(db.DateTime)
#     refresh_expires = db.Column(db.DateTime)
#
#     def __init__(self, access_token, refresh_token, expires, refresh_expires):
#         self.access_token = access_token
#         self.refresh_token = refresh_token
#         self.expires = expires
#         self.refresh_expires = refresh_expires
#
#
# class Grant(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     client_id = db.Column(db.String(40), index=True, nullable=False)
#     code = db.Column(db.String(255), index=True, nullable=False)
#     redirect_uri = db.Column(db.String(255))
#     user_id = db.Column(db.Integer, index=True)
#     expires = db.Column(db.DateTime)
#     scope = db.Column(db.String(255))
#     grant_type = db.Column(db.String(255))
#
#     def __repr__(self):
#         return '<Grant %r>' % self.id
#

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    is_available = db.Column(db.Boolean, default=True)


class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book


class Checkout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)


class CheckoutSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Checkout


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    # books_checked_out = db.relationship('Checkout', backref='id', lazy=True)
    # checked_out_books = db.relationship('Checkout', backref='user', lazy=True)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


book_schema = BookSchema()
books_schema = BookSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)


checkout_schema = CheckoutSchema()
checkouts_schema = CheckoutSchema(many=True)


@app.route('/api/register', methods=['POST'])
def register():
    if 'username' not in request.json:
        return make_response(({'error': 'Missing required parameter: username'}), 400)
    if 'email' not in request.json:
        return make_response(({'error': 'Missing required parameter: email'}), 400)
    if 'password' not in request.json:
        return make_response(({'error': 'Missing required parameter: password'}), 400)

    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    is_admin = request.json.get('is_admin', False)

    # validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return make_response(({'error': 'Invalid email format'}), 400)

    user = User(username=username, email=email, password=password, is_admin=is_admin)
    print(user)

    try:
        db.session.add(user)
        db.session.commit()
        return make_response(({'message': 'User created successfully'}), 201)
    except:
        return make_response(({'error': 'Error creating user'}), 500)


@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return books_schema.jsonify(books)


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return make_response("Invalid book", 400)
    return make_response(book_schema.jsonify(book), 200)


@app.route('/api/books', methods=['POST'])
def add_book():
    title = request.json['title']
    author = request.json['author']

    print(request)
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


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def remove_book(book_id):
    book = Book.query.get(book_id)

    try:
        db.session.delete(book)
        db.session.commit()
        return make_response(book_schema.jsonify(book), 200)
    except:
        return make_response("Error removing book", 500)


@app.route('/api/checkout', methods=['POST'])
def checkout_book():
    user_id = request.json['user_id']
    book_id = request.json['book_id']

    if not user_id or not book_id:
        return make_response("Missing parameter user or book in the request", 400)

    user = User.query.get(user_id)
    print(user)
    book = Book.query.get(book_id)
    print(book)

    if not user or not book:
        return make_response("Invalid user or book", 400)

    # if len(user.checked_out_books) >= 10:
    #     return make_response("User has already checked out the maximum number of books (10)", 500)

    if not book.is_available:
        return make_response("Book is not available for checkout", 500)

    checked = Checkout(book_id=book_id, user_id=user_id)
    print(checked)
    book = Book.query.get(book_id)
    print(book_id)
    try:
        db.session.add(checked)
        db.session.commit()
        book.is_available = False
        return make_response(checkout_schema.jsonify(book), 201)
    except:
        return make_response("Error checking out book", 500)


@app.route('/api/checkouts/<int:book_id>', methods=['PUT'])
def return_book(book_id):
    if not book_id:
        return make_response("Missing parameter book in the request", 400)
    # checkout = Checkout.query.get(checkout_id)
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


@app.route('/api/checkouts', methods=['GET'])
def get_checkouts():
    checkouts = Checkout.query.all()
    return make_response(checkouts_schema.jsonify(checkouts), 200)


@app.route('/api/books/<int:checkout_id>', methods=['GET'])
def get_user_checkouts(checkout_id):
    if not checkout_id:
        return make_response("Missing parameter checkout_id", 400)
    checkout = Checkout.query.get(checkout_id)
    if not checkout:
        make_response("Invalid checkout_id", 400)

    return make_response(checkouts_schema.jsonify(checkout), 200)


@app.route('/api/fines/<int:user_id>', methods=['GET'])
def get_user_fines(user_id):
    if not user_id:
        return make_response("Missing parameter user_id", 400)
    user = User.query.get(user_id)
    if not user:
        make_response("Invalid user", 400)

    checkouts = Checkout.query.filter_by(user_id=user_id)
    fine_amount = 0

    for checkout in checkouts:
        book = Book.query.get(checkout.book_id)
        days_overdue = (datetime.now() - checkout.checkout_date).days - 14
        if days_overdue > 0:
            fine_amount += days_overdue * 0.10

    return make_response({"fine_amount": fine_amount}, 200)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


