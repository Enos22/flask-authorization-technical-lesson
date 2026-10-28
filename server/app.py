#!/usr/bin/env python3

from flask import Flask, make_response, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from sqlalchemy import select

from models import db, User, UserSchema, Document, DocumentSchema

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
        user = db.session.execute(
            select(User).where(User.username == request.get_json()['username'])
        ).scalar_one_or_none()

        if user:
            session['user_id'] = user.id
            return UserSchema().dump(user)
        else:
            return {'message': 'Invalid login'}, 401

class CheckSession(Resource):

    def get(self):
        user = db.session.get(User, session.get('user_id'))
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
    if not session.get('user_id') and request.endpoint not in {'document_list', 'login', 'check_session'}:
        return {'error': 'Unauthorized'}, 401


class Document(Resource):
    def get(self, id):
        document = db.session.get(Document, id)
        return DocumentSchema().dump(document)

    def patch(self, id):
        document = db.session.get(Document, id)
        for attr in request.form:
            setattr(document, attr, request.form[attr])

        db.session.add(document)
        db.session.commit()

        response = make_response(
            DocumentSchema().dump(document),
            200
        )

        return response

    def delete(self, id):
        document = db.session.get(Document, id)

        db.session.delete(document)
        db.session.commit()

        response = make_response(
            {"message": "document successfully deleted"},
            200
        )
        return response


class DocumentList(Resource):
    def get(self):
        documents = db.session.execute(select(Document)).scalars().all()
        return [DocumentSchema().dump(document) for document in documents]

api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Logout, '/logout')
api.add_resource(Document, '/documents/<int:id>', endpoint='document')
api.add_resource(DocumentList, '/documents', endpoint='document_list')

if __name__ == '__main__':
    app.run(port=5555, debug=True)