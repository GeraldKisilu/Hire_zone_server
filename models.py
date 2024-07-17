from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(app, metadata=metadata)
CORS(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    role = db.Column(db.String, nullable=False)  # either 'job_seeker' or 'employer'
    employer_id = db.Column(db.Integer, db.ForeignKey('employers_table.id'), nullable=True)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey('job_seekers_table.id'), nullable=True)

    employer = db.relationship('Employer', back_populates='user', uselist=False)
    job_seeker = db.relationship('JobSeekers', back_populates='user', uselist=False)

    def __repr__(self):
        return f"User {self.username} with email {self.email} created successfully."

class Employer(db.Model):
    __tablename__ = 'employers_table'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String, nullable=False)
    industry = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    contact_email = db.Column(db.String, nullable=False)

    # Relationship with Jobs model
    jobs = db.relationship('Jobs', back_populates='employer', lazy=True)
    job_seekers = db.relationship('JobSeekers', secondary='employer_job_seekers', back_populates='employers', lazy=True)
    user = db.relationship('User', back_populates='employer', uselist=False)

    def __repr__(self):
        return f"Employer with the ID of {self.id}, company name of {self.company_name} and the industry of {self.industry} successfully created."

class JobSeekers(db.Model):
    __tablename__ = 'job_seekers_table'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    middle_name = db.Column(db.String)
    email = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    details = db.relationship('JobSeekersDetails', back_populates='job_seeker', lazy=True)

    employers = db.relationship('Employer', secondary='employer_job_seekers', back_populates='job_seekers', lazy=True)
    user = db.relationship('User', back_populates='job_seeker', uselist=False)

    def __repr__(self):
        return f"Job Seeker with the ID of {self.id}, and name of {self.first_name} {self.last_name} successfully created."

class JobSeekersDetails(db.Model):
    __tablename__ = 'job_seekers_details'

    id = db.Column(db.Integer, primary_key=True)
    resume_url = db.Column(db.String, nullable=False)
    skills = db.Column(db.String, nullable=False)
    education_level = db.Column(db.String, nullable=False)
    work_experience = db.Column(db.String, nullable=False)
    portfolio_url = db.Column(db.String, nullable=False)
    jobseeker_id = db.Column(db.Integer, db.ForeignKey('job_seekers_table.id'), nullable=False, unique=True)

    job_seeker = db.relationship('JobSeekers', back_populates='details')

    def __repr__(self):
        return "Job Seeker's details added successfully."

class Jobs(db.Model):
    __tablename__ = 'jobs_table'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('employers_table.id'), nullable=False)

    employer = db.relationship('Employer', back_populates='jobs', lazy=True)

    def __repr__(self):
        return f"Job with the ID of {self.id}, title of {self.title} created successfully."

class EmployerJobSeekersConnector(db.Model):
    __tablename__ = 'employer_job_seekers'

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employers_table.id'), nullable=False)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey('job_seekers_table.id'), nullable=False)

    def __repr__(self):
        return f"EmployerJobSeekersConnector between employer ID {self.employer_id} and job seeker ID {self.job_seeker_id} created successfully."

# API Endpoints
@app.route('/jobseekers', methods=['POST'])
def create_jobseeker():
    data = request.json
    new_jobseeker = JobSeekers(
        first_name=data['first_name'],
        last_name=data['last_name'],
        middle_name=data.get('middle_name', ''),
        email=data['email'],
        phone_number=data['phone_number']
    )
    db.session.add(new_jobseeker)
    db.session.commit()
    return jsonify({"id": new_jobseeker.id, "message": "Jobseeker successfully created"}), 201

@app.route('/details', methods=['POST'])
def create_jobseeker_details():
    data = request.form
    academic_certificate = request.files.get('academic_certificate')
    cv = request.files.get('cv')

    academic_certificate_filename = f"uploads/academic_certificate_{data['jobseeker_id']}.pdf"
    cv_filename = f"uploads/cv_{data['jobseeker_id']}.pdf"

    academic_certificate.save(academic_certificate_filename)
    cv.save(cv_filename)

    new_details = JobSeekersDetails(
        resume_url=data['resume_url'],
        skills=data['skills'],
        education_level=data['education_level'],
        work_experience=data['work_experience'],
        portfolio_url=data['portfolio_url'],
        jobseeker_id=data['jobseeker_id'],
        academic_certificate=academic_certificate_filename,
        cv=cv_filename
    )
    db.session.add(new_details)
    db.session.commit()
    return jsonify({"message": "Job Seeker details added successfully."}), 201

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)