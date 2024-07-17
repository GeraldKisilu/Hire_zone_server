from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource, reqparse
from models import User, db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager, create_refresh_token, jwt_required, current_user
from functools import wraps

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')
bcrypt = Bcrypt()
jwt = JWTManager()
auth_api = Api(auth_bp)

def allow(*allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user = current_user
            roles = [role.name for role in user.roles]
            for role in allowed_roles:
                if role in roles:
                    return fn(*args, **kwargs)
            else:
                return {"msg": "Access Denied"}, 403

        return decorator

    return wrapper

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).first()

register_args = reqparse.RequestParser()
register_args.add_argument('email', type=str, required=True, help='Email is required')
register_args.add_argument('password', type=str, required=True, help='Password is required')
register_args.add_argument('username', type=str, required=True, help='Username is required')
register_args.add_argument('role', type=str, required=True, help='Role is required')
register_args.add_argument('employer_id', type=int)
register_args.add_argument('job_seeker_id', type=int)

login_args = reqparse.RequestParser()
login_args.add_argument('email', type=str, required=True, help='Email is required')
login_args.add_argument('password', type=str, required=True, help='Password is required')

class Register(Resource):
    def post(self):
        data = register_args.parse_args()
        if User.query.filter_by(email=data['email']).first():
            return {"msg": "Email is already registered!"}, 400
        if User.query.filter_by(username=data['username']).first():
            return {"msg": "Username is already taken!"}, 400
        
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(
            email=data['email'], 
            username=data['username'], 
            password=hashed_password, 
            role=data['role'], 
            employer_id=data.get('employer_id'), 
            job_seeker_id=data.get('job_seeker_id')
        )
        db.session.add(new_user)
        db.session.commit()

        return {"msg": 'User created successfully'}, 201

class Login(Resource):
    def post(self):
        data = login_args.parse_args()
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return {"msg": "User does not exist in our database"}, 400
        if not bcrypt.check_password_hash(user.password, data['password']):
            return {"msg": "Password is incorrect!"}, 400

        token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return {"token": token, "refresh_token": refresh_token}, 200

    @jwt_required(refresh=True)
    def get(self):
        token = create_access_token(identity=current_user.id)
        return {"token": token}, 200

auth_api.add_resource(Register, '/register')
auth_api.add_resource(Login, '/login')
