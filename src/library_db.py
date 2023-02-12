
from flask import Flask, request, make_response
from flask_oauthlib.provider import OAuth2Provider
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://libuser:library123@localhost/library_management'
db = SQLAlchemy(app)
oauth = OAuth2Provider(app)
ma = Marshmallow(app)


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
    is_admin = db.Column(db.Boolean, default=False)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


book_schema = BookSchema()
books_schema = BookSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)


checkout_schema = CheckoutSchema()
checkouts_schema = CheckoutSchema(many=True)


@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return books_schema.jsonify(books)


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    return book_schema.jsonify(book)


@app.route('/api/books', methods=['POST'])
def add_book():
    title = request.json['title']
    author = request.json['author']

    book = Book(title=title, author=author)

    try:
        db.session.add(book)
        db.session.commit()
        return make_response(book_schema.jsonify(book), 201)
    except:
        return make_response("Error adding book", 500)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


