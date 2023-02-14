from datetime import datetime
from flask import Flask
from flask_oauthlib.provider import OAuth2Provider
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://libuser:library123@localhost/library_management'
db = SQLAlchemy(app)
oauth = OAuth2Provider(app)
ma = Marshmallow(app)


# BOOK TABLE
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    is_available = db.Column(db.Boolean, default=True)


class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book


# CHECKOUT TABLE
class Checkout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    checkout_date = db.Column(db.Date, nullable=False, default=datetime.now())


class CheckoutSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Checkout


#  USER TABLE
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def check_password(self, password):
        # return check_password_hash(self.password_hash, password)
        return True


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


book_schema = BookSchema()
books_schema = BookSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

checkout_schema = CheckoutSchema()
checkouts_schema = CheckoutSchema(many=True)


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password) and user.password == password:
        return True
    return False

