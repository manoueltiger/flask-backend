from app import app, db
from app.models import Session, Patient, RehabilitationProgram, RehabilitationProgramStep, MedicalCare, ExerciseSession
from flask import request, jsonify, make_response
from datetime import date
from flask_cors import cross_origin
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()

@app.route("/api/mobile/session", methods=['GET'])
def hello_world():
    print('hello world')

@app.route("/api/mobile/sessions", methods=['POST'])
@cross_origin()
@scheduler.scheduled_job('cron', hour=0)
def create_sessions():
    #creation d'une variable avec la date du jour
    current_date = date.today().strftime('%d-%m-%Y')

    #rechercher tous les patients en cours de rehab
    patients_in_rehabilitation = Patient.query.filter_by(rehabilitation_in_progress=True).all()

    #ajouter une ligne supplémentaire à la date du jour à tous les patients en cours de rehab
    for patient in patients_in_rehabilitation:
        previous_session = Session.query.filter_by(patient_id=patient.id).order_by(Session.session_id.desc()).first()

        new_session = Session(patient_id=patient.id, date=current_date)
        new_session.number_of_days = previous_session.number_of_days + 1
        db.session.add(new_session)
        db.session.commit()

    return make_response(jsonify({'message': 'Session créée avec succès'}), 200)

scheduler.start()

@app.route("/api/mobile/check_session_exists", methods=['POST'])
def check_session_exists():
    patient_id = request.json.get('patient_id', None)
    session = Session.query.filter_by(patient_id=patient_id).order_by(Session.id.desc()).first()

    if session is None:
        return jsonify({'has_session': False, 'session_info': None})
    else:
        return jsonify({'has_session':True,
                        'session_info': {
                            'session_id': session.id,
                            'date': session.date,
                            'number_of_days': session.number_of_days,
                            'current_step': session.current_step,
                            'rehabilitation_program_id': session.rehabilitation_program_id
                        }})


@app.route("/api/mobile/get_current_session/<int:patient_id>", methods=['GET'])
def get_current_session_id(patient_id):

    session = Session.query.filter_by(patient_id=patient_id).order_by(Session.id.desc()).first()

    if session:
        return jsonify({
            'session_info': {
                'session_id': session.id,
                'date': session.date,
                'number_of_days': session.number_of_days,
                'current_step': session.current_step,
                'rehabilitation_program_id': session.rehabilitation_program_id
            }
        })
    else:
        return jsonify({'error': 'Aucune session retrouvée pour ce patient'})


@app.route("/api/mobile/create_first_session", methods=['POST'])
@cross_origin()
def create_first_session():
    patient_id = request.json.get('patient_id', None)
    if not patient_id:
        return make_response(jsonify({'error': 'Erreur : un patient_id est requis.'}), 400)

    patient = Patient.query.get(patient_id)
    if not patient:
        return make_response(jsonify({'error': 'Patient introuvable'}), 404)

    medical_care = MedicalCare.query.get(patient.medical_care_id)
    if not medical_care:
        return make_response(jsonify({'error': 'Prise en charge introuvable'}), 404)

    rehabilitation_program = RehabilitationProgram.query.filter_by(medical_care_id=medical_care.id).first()
    if not rehabilitation_program:
        return make_response(jsonify({'error': 'Programme de rééducation introuvable'}), 404)

    existing_session = Session.query.filter_by(patient_id=patient_id).first()

    if existing_session:
        return make_response(jsonify({'message': 'Ce patient a déja une session'}), 400)

    today = date.today().strftime('%d-%-m-%Y')
    new_session = Session(patient_id=patient_id, rehabilitation_program_id=rehabilitation_program.id, date=today)
    patient.rehabilitation_in_progress = True

    db.session.add(new_session)
    db.session.commit()

    return make_response(jsonify({'has_session':True, 'session_id': new_session.id}), 200)


@app.route("/api/mobile/update_current_step_rehabilitation/<int:session_id>", methods=['POST'])
def update_current_step_rehabilitation(session_id):

    session = Session.query.get(session_id)
    total_days = session.number_of_days

    rehab_program = RehabilitationProgram.query.get(session.rehabilitation_program_id)
    current_step = session.current_step
    days_elapsed = 0

    for step in rehab_program.steps:
        days_elapsed += step.duration
        if total_days <= days_elapsed:
            break

        current_step += 1

    session.current_step = current_step
    db.session.commit()

    return jsonify({'message': "Mise à jour de l'étape de rééducation"})

@app.route("/api/mobile/session/exercise_done", methods = ['POST'])
def increment_count_exercice_per_session():
    session_id = request.json.get('session_id', None)
    exercise_id = request.json.get('exercise_id', None)


