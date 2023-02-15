from app.api.library_apis import app, db

if __name__ == '__main__':
    with app.app_context():

        db.session.remove()
        db.drop_all()
    # app.run(debug=True)
