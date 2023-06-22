from flask import request, jsonify, make_response
from app import app, db
from app.models import Patient, Session, ExerciseUsage
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_cors import cross_origin
from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()


@app.route("/api/mobile/confirm_patient", methods=['POST'])
@cross_origin()
def confirm_patient():
    email = request.json.get('email', None)
    confirmation_token = request.json.get('confirmationToken', None)

    if not email:
        return make_response(jsonify({'error': 'Email manquant'}), 400)

    if not confirmation_token:
        return make_response(jsonify({'error': 'Le code reçu par mail n\'est pas renseigné'}), 400)

    patient = Patient.query.filter_by(email=email).first()

    if patient is None:
        return make_response(jsonify({'error': 'Utilisateur introuvable'}), 404)

    try:
        access_token = create_access_token(identity=patient.id)
        return make_response(jsonify({'token': access_token, 'user': {
            'id': patient.id,
            'firstname': patient.firstname,
            'lastname': patient.lastname,
            'email': patient.email,
        }}), 200)
    except JWTExtendedException as error:
        return make_response(jsonify({'error': "Erreur lors de la création du jeton"}), 500)


@app.route("/api/mobile/change_password", methods=['POST'])
@cross_origin()
@jwt_required()
def change_password_after_confirmation():
    patient_id = get_jwt_identity()
    patient = Patient.query.get(patient_id)

    if not patient:
        return make_response(jsonify({'error': 'Patient introuvable'}), 404)
    print(patient)

    patient.password = request.json.get('new_password', None)

    db.session.commit()
    try:
        access_token = create_access_token(identity=patient.id)
        return make_response(jsonify({'token': access_token, 'message': 'Mot de passe modifié', 'user': {
            'id': patient.id,
            'firstname': patient.firstname,
            'lastname': patient.lastname,
            'email': patient.email,
        }}), 200)
    except JWTExtendedException as error:
        return make_response(jsonify({'error': "Erreur lors du changement du pot de passe"}), 500)


@app.route("/api/mobile/login", methods=["POST"])
@cross_origin()
def login_patient_on_app():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email:
        return make_response(jsonify({'error': 'Email manquant'}), 400)

    if not password:
        return make_response(jsonify({'error': 'Mot de passe manquant'}), 400)

    patient = Patient.query.filter_by(email=email).first()

    if patient is None:
        return make_response(jsonify({'error': 'Utilisateur introuvable'}), 404)

    print(patient)
    # if not check_password_hash(patient.password, password):
    #     return make_response(jsonify({'error': 'Mot de passe incorrect'}), 401)

    try:
        access_token = create_access_token(identity=patient.id)
        return make_response(jsonify({'token': access_token, 'user': {
            'id': patient.id,
            'firstname': patient.firstname,
            'lastname': patient.lastname,
            'email': patient.email,
            'socialSecurityNumber': patient.ssn
        }}), 200)
    except JWTExtendedException as error:
        return make_response(jsonify({'error': "Erreur lors de la création du jeton"}), 500)


@app.route("/api/mobile/sessions", methods=['POST'])
@cross_origin()
@scheduler.scheduled_job('cron', hour=0)
def create_sessions():
    current_date = date.today().strftime('%d-%m-%Y')

    patients_in_rehabilitation = Patient.query.filter_by(rehabilitation_in_progress=True).all()

    for patient in patients_in_rehabilitation:
        new_session = Session(patient_id=patient.id, date=current_date)
        db.session.add(new_session)
        db.session.commit()

    return make_response(jsonify({'message': 'Session créée avec succès'}), 200)


scheduler.start()


@app.route("/api/mobile/exercices/<exercise_id>/complete", methods=["POST"])
@cross_origin()
def complete_exercise(exercise_id):
    patient_id = get_jwt_identity()
    date = request.json.get('date', None)

    if date is None:
        return make_response(jsonify({'error': 'Erreur dans la date envoyée dans la requête'}), 400)

    session = Session.query.filter_by(patient_id=patient_id, date=date).first()

    if session is None:
        return make_response(jsonify({'error': 'Session introuvable'}), 404)

    session_id = session.id

    exercise_usage = ExerciseUsage.query.filter_by(session_id=session_id, exercise_id=exercise_id).first()

    if exercise_usage is None:
        return make_response(jsonify({'error': 'la variable exerciseUsage est introuvable'}), 404)

    exercise_usage.count += 1
    db.session.commit()

    return make_response(jsonify({'message': "Compteur de lecture d'exercice incrémenté avec succès"}), 200)