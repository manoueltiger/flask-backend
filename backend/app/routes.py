from flask import request, jsonify, make_response
from app import app, db, mail
from app.models import User, Patient, Pathology, MedicalCare
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_cors import cross_origin
from flask_mail import Message
from sqlalchemy import desc
import random, secrets


@app.route('/api', methods=['GET'])
@cross_origin()
def api():
    return jsonify({'message': 'API is up and running'})

@app.route('/api_post', methods=["POST"])
@cross_origin()
def api_post():
    family_name = request.json.get('family_name', None)

    if family_name == "manu":
        return make_response(jsonify({'message': f'Bonjour {family_name} ! API is up and running'}), 200)

    return make_response(jsonify({'message': "Vous n'avez pas d'utilisateur manu enregistré dans la base !"}))

@app.route("/api/login", methods=["POST"])
@cross_origin()
def login_user():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email:
        return make_response(jsonify({"error": "Email manquant"}), 400)

    if not password:
        return make_response(jsonify({'error': 'Mot de passe manquant'}), 400)

    user = User.query.filter_by(email=email).first()
    print(user.id)

    if user is None:
        return make_response(jsonify({"error": "Utilisateur introuvable"}), 404)

    if not check_password_hash(user.password, password):
        return make_response(jsonify({"error": "Mot de passe incorrect"}), 401)

    try:
        access_token = create_access_token(identity=user.id)
        return make_response(jsonify({'token': access_token, 'user': {
            'id': user.id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'email': user.email,
            'rpps': user.rpps,
            'speciality': user.speciality
        }}), 200)
    except JWTExtendedException as error:
        return make_response(jsonify({'error': "Erreur lors de la création du jeton"}), 500)


@app.route('/api/logout', methods=['POST'])
def logout_user():
    return make_response(jsonify({'message': "L'utilisateur s'est déconnecté"}), 200)


@app.route("/api/signup", methods=["POST"])
@cross_origin()
def signup_user():
    firstname = request.json.get('firstname', None)
    lastname = request.json.get('lastname', None)
    email = request.json.get('email', None)
    rpps = request.json.get('rpps', None)
    speciality = request.json.get('speciality', None)
    password = request.json.get('password', None)

    user_exists = User.query.filter_by(email=email).first()

    if user_exists:
        return make_response(jsonify({'erreur': "Un compte avec cet email existe déja !"}), 409)

    password_hash = generate_password_hash(password, method='sha256')
    confirmation_token = secrets.token_hex(32)

    new_user = User(firstname=firstname,
                    lastname=lastname,
                    email=email,
                    rpps=rpps,
                    speciality=speciality,
                    password=password_hash,
                    confirmation_token=confirmation_token,
                    confirmed=False)

    confirmation_url = f"http://localhost:3000/confirm/{confirmation_token}"

    # construire le message du mail
    subject = "Inscription sur l'application de santé"
    body = f"Bonjour Dr {firstname} {lastname},\n\nBienvenue sur l'application santé d'auto-rééducation et " \
           f"merci de vous être inscrit.\n\n" \
           f"Un email de confirmation a été envoyé à votre adresse e-mail : {email}.\n\n" \
           f"Cliquez sur le lien suivant pour confirmer votre adresse e-mail et accéder à votre compte :\n" \
           f"{confirmation_url}\n\n" \
           f"Cordialement,\nL'équipe de l'application de santé"
    message = Message(subject, sender='emmanuel.tigier@gmail.com', recipients=[email], body=body)

    # envoyer le mail avec Flask-Mail
    mail.send(message)
    db.session.add(new_user)
    db.session.commit()

    try:
        access_token = create_access_token(identity=new_user.id)
        return make_response(jsonify({'token': access_token,
                                  'user': {
                                      'id': new_user.id,
                                      'firstname': new_user.firstname,
                                      'lastname': new_user.lastname,
                                      'email': new_user.email,
                                      'rpps': new_user.rpps,
                                      'speciality': new_user.speciality
                                  },
                                  'message': "Utilisateur créé en attente de confirmation"}), 200)
    except JWTExtendedException as error:
        return make_response(jsonify({'error': "Erreur lors de l'inscription"}), 500)


@app.route("/api/confirm/<token>", methods=['GET'])
@cross_origin()
def confirm_user(token):
    user = User.query.filter_by(confirmation_token=token).first()

    if user:
        user.confirmed = True  # Mark the user as confirmed
        user.confirmation_token = None  # Clear the confirmation token
        db.session.commit()
        access_token = create_access_token(identity=user.id)


        #renvoyer un message de succès vers le front qui ira vers le formulaire de connexion
        return make_response(jsonify({'token': access_token,
                                      'message': "Inscription de l'utilisateur confirmée avec succès"}), 200)
    else:
        return make_response(jsonify({'error': "Lien de confirmation invalide"}), 400)


@app.route("/api/user", methods=['GET'])
@jwt_required()
@cross_origin()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return make_response(jsonify({'message': "Utilisateur introuvable"}), 404)

    return make_response(jsonify({
        'firstname': user.firstname,
        'lastname': user.lastname,
        'email': user.email,
        'rpps': user.rpps,
        'speciality': user.speciality

    }), 200)


@app.route("/api/update", methods=['PUT'])
@jwt_required()
@cross_origin()
def update_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return make_response(jsonify({'error': 'Utilisateur introuvable'}), 404)

    user.firstname = request.json.get('firstname', user.firstname)
    user.lastname = request.json.get('lastname', user.lastname)
    user.email = request.json.get('email', user.email)
    user.rpps = request.json.get('rpps', user.rpps)
    user.speciality = request.json.get('speciality', user.speciality)

    db.session.commit()

    try:
        return jsonify({'message': 'Utilisateur mis à jour',
                                      'user': {
                                          'id': user.id,
                                          'firstname': user.firstname,
                                          'lastname': user.lastname,
                                          'email': user.email,
                                          'rpps': user.rpps,
                                          'speciality': user.speciality
                                        }
                                      })
    except JWTExtendedException:
        return make_response(jsonify({'error': "Erreur lors de la mise à jour du profil"}), 500)


@app.route("/api/delete", methods=['DELETE'])
@jwt_required()
@cross_origin()
def delete_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return make_response(jsonify({'error': 'Utilisateur introuvable'}), 404)

    user.delete()

    return make_response(jsonify({'message': 'Utilisateur supprimé'}), 200)


@app.route("/api/new_patient", methods=["POST"])
@cross_origin()
def create_patient():
    firstname = request.json.get('firstname', None)
    lastname = request.json.get('lastname', None)
    email = request.json.get('email', None)
    phone = request.json.get('phone', None)
    ssn = request.json.get('socialSecurityNumber', None)
    birthdate = request.json.get('birthDate', None)
    pathology_id = request.json.get('pathologyId', None)
    medical_care_id = request.json.get('medicalCareId', None)
    user_id = request.json.get('user_id', None)

    patient_exists = Patient.query.filter_by(firstname=firstname, lastname=lastname, ssn=ssn).first()

    if patient_exists:
        return make_response(jsonify({'error': "Cet utilisateur existe déja !"}), 409)

    password = ''.join(random.choices('0123456789', k=8))

    new_patient = Patient(firstname=firstname, lastname=lastname, email=email, phone=phone,
                          password=password, ssn=ssn, birthdate=birthdate, pathology_id=pathology_id,
                          medical_care_id=medical_care_id ,user_id=user_id)

    # construire le message du mail
    subject = "Bienvenue sur l'application de santé"
    body = f"Bonjour {firstname} {lastname},\n\nVoici le lien vers l'application : https://example.com/app\n\nVotre " \
           f"mot de passe est : {password}\n\nCordialement,\nL'équipe de l'application de santé"
    message = Message(subject, sender='emmanuel.tigier@gmail.com', recipients=[email], body=body)

    # envoyer le mail avec Flask-Mail
    mail.send(message)
    db.session.add(new_patient)
    db.session.commit()

    return make_response(jsonify({'message': "Utilisateur créé avec succès"}), 200)

@app.route("/api/patients/<int:user_id>", methods=["GET"])
@cross_origin()
def get_user_patients(user_id):
    patients = Patient.query.filter_by(user_id=user_id).all()
    result = []
    for patient in patients:
        medical_care = MedicalCare.query.get(patient.medical_care_id)
        pathology = Pathology.query.get(patient.pathology_id)
        patient_data = {
            "id": patient.id,
            "firstname": patient.firstname,
            "lastname": patient.lastname,
            "socialSecurityNumber": patient.ssn,
            "email": patient.email,
            "pathology_id": patient.pathology_id,
            "medical_care_id": patient.medical_care_id,
            "user_id": patient.user_id,
            "medicalCare": medical_care.name if medical_care else None,
            "pathology": pathology.name if pathology else None
        }
        result.append(patient_data)
    return make_response(jsonify(result))

@app.route("/api/last_patients_order/<int:user_id>", methods=["GET"])
@cross_origin()
def get_user_last_patients(user_id):
    patients = Patient.query.filter_by(user_id=user_id).order_by(desc(Patient.id)).limit(8).all()
    result = []
    for patient in patients:
        medical_care = MedicalCare.query.get(patient.medical_care_id)
        pathology = Pathology.query.get(patient.pathology_id)
        patient_data = {
            "id": patient.id,
            "firstname": patient.firstname,
            "lastname": patient.lastname,
            "socialSecurityNumber": patient.ssn,
            "email": patient.email,
            "pathology_id": patient.pathology_id,
            "medical_care_id": patient.medical_care_id,
            "user_id": patient.user_id,
            "medicalCare": medical_care.name if medical_care else None,
            "pathology": pathology.name if pathology else None
        }
        result.append(patient_data)

    return make_response(jsonify(result))

@app.route("/api/patient/<int:patientId>", methods=["GET"])
@cross_origin()
def get_patient(patientId):
    patient = Patient.query.get(patientId)

    if not patient:
        return make_response(jsonify({"error": "Patient introuvable"}), 404)

    if patient is None:
        return make_response(jsonify({"error": "Cet utilisateur n'existe pas !"}))

    patient_details = {
        "id": patient.id,
        "firstname": patient.firstname,
        "lastname": patient.lastname,
        "email": patient.email,
        "socialSecurityNumber": patient.ssn,
        "pathology_id": patient.pathology_id,
        "user_id": patient.user_id,
    }
    print(patient_details)

    return make_response(jsonify({"patient": patient_details}))


@app.route("/api/patient/<int:patientId>", methods=["PUT"])
@cross_origin()
def update_user_patient(patientId):
    patient = Patient.query.get(patientId)

    if not patient:
        return make_response(jsonify({"error": "Patient introuvable"}), 404)

    patient.firstname = request.json.get('firstname', patient.firstname)
    patient.lastname = request.json.get('lastname', patient.lastname)
    patient.ssn = request.json.get('socialSecurityNumber', patient.ssn)
    patient.email = request.json.get('email', patient.email)
    patient.user_id = request.json.get('user_id', patient.user_id)

    db.session.commit()

    return jsonify({'message': "Patient mis à jour ",
                                  'patient': {
                                      'id': patient.id,
                                      'firstname': patient.firstname,
                                      'lastname': patient.lastname,
                                      'socialSecurityNumber': patient.ssn,
                                      'email': patient.email,
                                      'user_id': patient.user_id
                                  }})


@app.route("/api/delete_patient/<int:id>", methods=["DELETE"])
@cross_origin()
def delete_user_patient(id):
    patient = Patient.query.get(id)

    if not patient:
        return make_response(jsonify({"error": "Patient introuvable"}), 404)

    db.session.delete(patient)
    db.session.commit()

    return make_response(jsonify({'message': "Patient supprimé "}), 200)


@app.route("/send_mail", methods=['GET'])
def send_mail():
    msg = Message('Hello', sender='emmanuel.tigier@gmail.com', recipients=['emmanuel.tigier@me.com'])
    msg.body = "Test d'envoi de mail"
    mail.send(msg)
    return 'Mail envoyé !'


