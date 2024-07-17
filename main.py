from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db
from employers import  employer_bp
from jobseekers import jobseeker_bp
from jobseekersdetails import details_bp
from jobs import jobs_bp
from auth import auth_bp
from auth import jwt



app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Hire-zone.db'

# Creating a secret key
app.config['SECRET_KEY'] = '12345678'

# create database called jobs
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(employer_bp)
app.register_blueprint(jobseeker_bp)
app.register_blueprint(details_bp)
app.register_blueprint(jobs_bp)
app.register_blueprint(auth_bp)

jwt.init_app(app)

db.init_app(app)
migrate = Migrate(app=app, db=db)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)