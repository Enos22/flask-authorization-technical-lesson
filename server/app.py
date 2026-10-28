#!/usr/bin/env python3

from flask import Flask, make_response, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, User, UserSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Login(Resource):

    def post(self):
        user = User.query.filter(
            User.username == request.get_json()['username']
        ).first()
        
        if user:
            session['user_id'] = user.id
            return UserSchema().dump(user)
        else:
            return {'message': 'Invalid login'}, 401

class CheckSession(Resource):

    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return UserSchema().dump(user)
        else:
            return {'message': '401: Not Authorized'}, 401

class Logout(Resource):

    def delete(self):
        session['user_id'] = None
        return {'message': '204: No Content'}, 204

@app.before_request
def check_if_logged_in():
        if not session['user_id']:
            return {'error': 'Unauthorized'}, 401
        
class Document(Resource):
    def get(self, id):
        document = Document.query.filter(Document.id == id).first()
        return DocumentSchema().dump(document)

    def patch(self, id):   
        document = Document.query.filter(Document.id == id).first()
        for attr in request.form:
            setattr(record, attr, request.form[attr])

        db.session.add(document)
        db.session.commit()

        response = make_response(
            DocumentSchema().dump(document),
            200
        )

        return response

    def delete(self, id):
        document = Document.query.filter(Document.id == id).first()
        
        db.session.delete(document)
        db.session.commit()

        response = make_response(
            {"message": "document successfully deleted"},
            200
        )
        return response 


api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Logout, '/logout')
api.add_resource(Document, '/documents/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)