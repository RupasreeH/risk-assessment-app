from flask import make_response, request, jsonify, Blueprint
from flask_login import login_user, logout_user, current_user, login_required

import uuid

from riskassessmentapp.extensions import db, bcrypt

from riskassessmentapp.users.models import User

users = Blueprint('users', __name__, template_folder='templates')

@users.route('/')
def index():
    if current_user.is_authenticated:
        return str(current_user.email)
    else:
        return 'No user is logged in'

@users.route('/signup', methods=['POST'])
def signup():
    if "firstName" not in request.json or "lastName" not in request.json or "email" not in request.json or "password" not in request.json:
        response = make_response(jsonify({'message': 'Fields are missing'}))
        response.status_code = 400
        response.headers['content-type'] = 'application/json' 
        return response
    
    first_name = request.json['firstName']
    last_name = request.json['lastName']
    email = request.json['email']
    password = request.json['password']

    user = User.query.filter(User.email == email).first()

    if user:
        response = make_response(jsonify({'message': 'User already exists!'}))
        response.status_code = 400
        response.headers['content-type'] = 'application/json'
        return response

    uid = uuid.uuid4()

    hashed_password = bcrypt.generate_password_hash(password)

    user = User(first_name = first_name, last_name = last_name, email = email, password=hashed_password, uid=uid)

    db.session.add(user)
    db.session.commit()

    response = make_response(jsonify({'message': 'Successfully written!', 'user':user.to_json_response()}))
    response.status_code = 200
    response.headers['content-type'] = 'application/json'
    return response

@users.route('/login', methods=['POST'])
def login():
    if "email" not in request.json or "password" not in request.json:
        response = make_response(jsonify({'message': 'Fields are missing', 'user':{}}))
        response.status_code = 400
        response.headers['content-type'] = 'application/json' 
        return response

    email = request.json['email']
    password = request.json['password']

    user = User.query.filter(User.email == email).first()

    if not user:
        response = make_response(jsonify({'message': 'User not found', 'user':{}}))
        response.status_code = 400
        response.headers['content-type'] = 'application/json'
        return response
    
    if bcrypt.check_password_hash(user.password, password):
        login_user(user)
        response = make_response(jsonify({'message': 'Logged in', 'user':user.to_json_response()}))
        response.status_code = 200
        response.headers['content-type'] = 'application/json'
    else:
        response = make_response(jsonify({'message': 'Failed to login', 'user':{}}))
        response.status_code = 400
        response.headers['content-type'] = 'application/json'

    return response

@users.route('/logout')
def logout():
    logout_user()
    return 'Success'