from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db
from employers import employer_bp
from jobseekers import jobseeker_bp
from jobseekersdetails import details_bp
from jobs import jobs_bp
from auth import auth_bp, jwt  # Ensure jwt is imported from auth.py
from datetime import timedelta
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Hire-zone.db'

# Creating a secret key
app.config['SECRET_KEY'] = '12345678'

# JWT Config
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize JWTManager with the app
jwt.init_app(app)

# Create database called jobs
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Register Blueprints
app.register_blueprint(employer_bp)
app.register_blueprint(jobseeker_bp)
app.register_blueprint(details_bp)
app.register_blueprint(jobs_bp)
app.register_blueprint(auth_bp)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app=app, db=db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)