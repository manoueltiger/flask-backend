from app import app, db
from app.models import Session, Patient, RehabilitationProgram, RehabilitationProgramStep
from flask import request, jsonify, make_response
from datetime import date
from flask_cors import cross_origin
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()


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


@app.route("/api/mobile/get_current_session", methods=['GET'])
def get_current_session_id(patient_id):
    session = Session.query.filter_by(patient_id=patient_id).order_by(Session.session_id.desc()).first()

    if session:
        session_id = session.id
        return jsonify({'session_id' : session_id})
    else:
        return jsonify({'error': 'Aucune session retrouvée pour ce patient'})


@app.route("/api/mobile/update_current_step_rehabilitation/<int:session_id>")
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
