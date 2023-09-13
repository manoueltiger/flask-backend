from flask import request, jsonify, make_response
from app import app, db
from app.models import Patient, Pathology, MedicalCare, Session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_cors import cross_origin
from datetime import date


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
            'socialSecurityNumber': patient.ssn,
            'pathology_id': patient.pathology_id,
            'medical_care_id': patient.medical_care_id
        }}), 200)
    except JWTExtendedException as error:
        return make_response(jsonify({'error': "Erreur lors de la création du jeton"}), 500)

@app.route("/api/mobile/get_pathology_and_care/<int:pathology_id>", methods=['GET'])
@cross_origin()
def get_pathology_and_care(pathology_id):
    pathology = Pathology.query.get(pathology_id)

    medical_care = MedicalCare.query.filter_by(pathology_id=pathology_id).first()

    return make_response(jsonify({'pathology' : pathology.name, 'medical_care' : medical_care.name}))


