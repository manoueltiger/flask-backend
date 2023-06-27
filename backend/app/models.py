from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(25), nullable=False)
    lastname = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(50), unique=True)
    rpps = db.Column(db.BigInteger)
    workplace = db.Column(db.String)
    speciality = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    confirmation_token = db.Column(db.String(100), unique=True)

    def __init__(self, firstname, lastname, email, rpps, speciality, password, confirmed, confirmation_token):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.rpps = rpps
        self.speciality = speciality
        self.password = password
        self.confirmed = confirmed
        self.confirmation_token = confirmation_token

    def __repr__(self):
        return '<User {}>'.format(self.firstname, self.lastname)

    def update_password(self, new_password):
        self.password = generate_password_hash(new_password, method='sha256')
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50))
    ssn = db.Column(db.BigInteger, nullable=False)
    birthdate = db.Column(db.String)
    phone = db.Column(db.String(20))
    password = db.Column(db.String)
    rehabilitation_in_progress = db.Column(db.Boolean, default=True)
    pathology_id = db.Column(db.Integer, db.ForeignKey('pathology.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pathology = db.relationship('Pathology')
    program = db.relationship('RehabilitationProgram')

    def __init__(self, firstname, lastname, email, phone, password, ssn, birthdate, pathology_id, user_id):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.phone = phone
        self.password = password
        self.ssn = ssn
        self.birthdate = birthdate
        self.pathology_id = pathology_id
        self.user_id = user_id

    def __delete__(self):
        db.session.delete(self)
        db.session.commit()


class Speciality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name


class LocationPathology(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    speciality_id = db.Column(db.Integer, db.ForeignKey('speciality.id'))

    def __init__(self, name, speciality_id):
        self.name = name
        self.speciality_id = speciality_id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'speciality_id': self.speciality_id
        }


class Pathology(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    location_pathology_id = db.Column(db.Integer, db.ForeignKey('location_pathology.id'), nullable=False)

    def __init__(self, name, location_pathology_id):
        self.name = name
        self.location_pathology_id = location_pathology_id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location_pathology_id': self.location_pathology_id
        }


class RehabilitationProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer, nullable=False)
    pathology_id = db.Column(db.Integer, db.ForeignKey('pathology.id'))
    steps = db.relationship('RehabilitationProgramStep', backref='rehabilitation_program', lazy=True)

    def __init__(self, name, description, start_date, pathology_id):
        self.name = name
        self.description = description
        self.start_date = start_date
        self.pathology_id = pathology_id


class RehabilitationProgramStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    duration = db.Column(db.Integer, nullable=False)
    rehabilitation_step_finished = db.Column(db.Boolean, default=False)
    step_number = db.Column(db.Integer)
    rehabilitation_program_id = db.Column(db.Integer, db.ForeignKey('rehabilitation_program.id'))
    exercises = db.relationship('Exercise', secondary='program_exercise')

    def __init__(self, name, duration, step_number, rehabilitation_program_id):
        self.name = name
        self.duration = duration
        self.step_number = step_number
        self.rehabilitation_program_id = rehabilitation_program_id


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    video_link = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    def __init__(self, title, description, video_link, duration):
        self.title = title
        self.description = description
        self.duration = duration
        self.video_link = video_link


class ProgramExercise(db.Model):
    program_step_id = db.Column(db.Integer, db.ForeignKey('rehabilitation_program_step.id'), primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), primary_key=True)


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String)
    number_of_days = db.Column(db.Integer, default= 1)
    completed = db.Column(db.Boolean, default=False)
    survey_completed = db.Column(db.Boolean, default=False)
    current_step = db.Column(db.Integer, default= 1)
    rehabilitation_program_id = db.Column(db.Integer, db.ForeignKey('rehabilitation_program.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))

    def __init__(self, patient_id):
        self.patient_id = patient_id

class ExerciseUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    count = db.Column(db.Integer, default=0)

    def __init__(self, session_id, exercise_id, count):
        self.session_id = session_id
        self.exercise_id = exercise_id
        self.count = count


class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_survey = db.Column(db.String, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)


class SurveyAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String)
    answer = db.Column(db.String)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))

