from flask import request, jsonify, make_response
from app import app, db
from app.models import User, Patient, Speciality, LocationPathology, Pathology, RehabilitationProgram, \
    RehabilitationProgramStep,  MedicalCare
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_cors import cross_origin


@app.route('/api/new_speciality', methods=['POST'])
def add_speciality():
    name = request.json.get('name', None)
    speciality = Speciality(name=name)

    db.session.add(speciality)
    db.session.commit()

    return make_response(jsonify({'message': 'Spécialité rajoutée avec succès'}), 201)


@app.route('/api/specialities', methods=['GET'])
def list_specialities():
    specialities = Speciality.query.all()
    result = []

    for speciality in specialities:
        s_data = {
            "id": speciality.id,
            "name": speciality.name
        }
        result.append(s_data)
    return jsonify(result)

@app.route('/api/new_sub_speciality', methods=['POST'])
def add_sub_speciality():
    name = request.json.get('name', None)
    speciality_id = request.json.get('speciality_id', None)

    sub_speciality_exists = LocationPathology.query.filter_by(name=name, speciality_id = speciality_id).first()

    if sub_speciality_exists:
        return make_response(jsonify({'error': "Cette sous-spécialité existe déja !"}), 409)

    new_sub_speciality = LocationPathology(name=name, speciality_id=speciality_id)
    db.session.add(new_sub_speciality)
    db.session.commit()

    return make_response(jsonify({'message': "Sous-spécialité créée avec succès"}), 200)

@app.route('/api/get_sub_specialities', methods=['GET'])
def list_sub_specialities():
    sub_specialities = LocationPathology.query.all()
    result = []

    for sub_speciality in sub_specialities:
        s_data = {
            "id": sub_speciality.id,
            "name": sub_speciality.name,
            "speciality_id": sub_speciality.speciality_id
        }
        result.append(s_data)
    return jsonify(result)

@app.route('/api/new_pathology', methods=['POST'])
def add_pathology():
    name = request.json.get('name', None)
    location_pathology_id = request.json.get('location_pathology_id', None)

    pathology_exists = Pathology.query.filter_by(name=name, location_pathology_id=location_pathology_id).first()

    if pathology_exists:
        return make_response(jsonify({'error': "Cette pathologie existe déja !"}), 409)

    new_pathology = Pathology(name=name, location_pathology_id=location_pathology_id)
    db.session.add(new_pathology)
    db.session.commit()

    return make_response(jsonify({'message': "Pathologie créée avec succès"}), 200)

@app.route('/api/sub_specialities', methods=['GET'])
def list_sub_specialities_by_speciality():
    speciality_id = request.args.get('speciality_id')
    if speciality_id is not None:
        sub_specialities = LocationPathology.query.filter_by(speciality_id=speciality_id).all()
        return jsonify([s.to_dict() for s in sub_specialities])
    else:
        return jsonify([])

@app.route('/api/pathologies', methods=['GET'])
def list_pathologies_by_sub_speciality():
    location_pathology_id = request.args.get('location_pathology_id')
    if location_pathology_id is not None:
        pathologies = Pathology.query.filter_by(location_pathology_id=location_pathology_id).all()
        return jsonify([s.to_dict() for s in pathologies])
    else:
        return jsonify([])


@app.route('/api/all_pathologies', methods=['GET'])
def get_all_pathologies():
    pathologies = Pathology.query.all()
    result = []

    for pathology in pathologies:
        pathology_data= {
            'id': pathology.id,
            'name': pathology.name,
        }
        result.append(pathology_data)

    return jsonify(result)

@app.route('/api/get_pathologies_programs', methods=['GET'])
@cross_origin()
def get_all_pathologies_and_programs():
    medical_cares = db.session.query(MedicalCare, RehabilitationProgram)\
        .join(RehabilitationProgram, MedicalCare.id==RehabilitationProgram.medical_care_id).all()

    results=[]
    id= 0

    for medical_care, program in medical_cares:
        result = {
            'id':id,
            'medical_care': medical_care.name,
            'duration': program.duration,
            'program': program.name
        }
        id+=1
        results.append(result)

    return jsonify(results)

@app.route('/api/medical_cares', methods=['GET'])
@cross_origin()
def list_medical_cares_by_pathology():
    pathology_id = request.args.get('pathology_id')
    if pathology_id is not None:
        medical_cares = MedicalCare.query.filter_by(pathology_id=pathology_id).all()
        return jsonify([s.to_dict() for s in medical_cares])
    else:
        return jsonify([])


@app.route('/api/get_pathologies_medical_cares', methods=['GET'])
@cross_origin()
def get_all_pathologies_and_cares():
    pathologies = db.session.query(Pathology, MedicalCare)\
        .join(MedicalCare, Pathology.id==MedicalCare.pathology_id).all()

    results=[]

    for pathology, medical_care in pathologies:
        result = {
            'id': medical_care.id,
            'pathology': pathology.name,
            'medical_care': medical_care.name
        }
        results.append(result)

    return jsonify(results)

@app.route('/api/new_rehab_program', methods=['POST'])
@cross_origin()
def add_rehab_program():
    name = request.json.get('name', None)
    description = request.json.get('description', None)
    duration = request.json.get('duration', None)
    medical_care_id = request.json.get('medical_care_id', None)

    rehab_program_exists = RehabilitationProgram.query.filter_by(name=name, description=description,
                                                                 medical_care_id=medical_care_id).first()

    if rehab_program_exists :
        return make_response(jsonify({'error': 'Ce programme existe déja ! '}), 409)

    new_rehab_program = RehabilitationProgram(name=name, description=description, duration=duration,
                                              medical_care_id=medical_care_id)
    db.session.add(new_rehab_program)
    db.session.commit()

    return make_response(jsonify({'message': 'Programme de rééducation créé avec succès'}), 200)

@app.route('/api/update_rehab_program', methods=['POST'])
@cross_origin()
def update_rehab_program():
    return make_response(jsonify({'message': 'succès'}), 200)

@app.route('/api/new_medical_care', methods=['POST'])
@cross_origin()
def add_new_medical_care():
    name = request.json.get('name', None)
    pathology_id = request.json.get('pathology_id', None)

    medical_care_exists = MedicalCare.query.filter_by(name=name, pathology_id=pathology_id).first()

    if medical_care_exists:
        return make_response(jsonify({'error': 'Cette prise en charge existe déja !'}), 409)

    new_medical_care = MedicalCare(name=name, pathology_id=pathology_id)
    db.session.add(new_medical_care)
    db.session.commit()

    return make_response(jsonify({'message': 'Prise en charge médicale ou chirurgicale créée avec succès !'}), 200)


@app.route('/api/all_medical_cares', methods =['GET'])
@cross_origin()
def get_all_medical_cares():
    medical_cares = MedicalCare.query.all()
    results = []

    for medical_care in medical_cares:
        result = {
            'id': medical_care.id,
            'name': medical_care.name,
        }
        results.append(result)

    return jsonify(results)

@app.route('/api/get_rehabilitation_programs', methods=['GET'])
@cross_origin()
def get_all_rehabilitation_programs():

    programs = RehabilitationProgram.query.all()
    results = []

    for program in programs:
        result = {
            'id': program.id,
            'name': program.name
        }
        results.append(result)

    return jsonify(results)

@app.route('/api/rehabilitation_program_steps', methods=['GET'])
@cross_origin()
def list_steps_by_rehabilitation_program():
    rehabilitation_program_id = request.args.get('program_id')

    if rehabilitation_program_id is not None:
        steps = RehabilitationProgramStep.query.filter_by(rehabilitation_program_id=rehabilitation_program_id).all()
        return jsonify([s.to_dict() for s in steps])
    else:
        return jsonify([])

@app.route('/api/new_rehab_program_step', methods=['POST'])
@cross_origin()
def add_new_rehabilitation_program_step():
    name = request.json.get('name', None)
    duration = request.json.get('duration', None)
    step_number = request.json.get('step_number')
    rehabilitation_program_id = request.json.get('rehabilitation_program_id', None)

    step_exists = RehabilitationProgramStep.query.filter_by(name=name, rehabilitation_program_id=rehabilitation_program_id,
                                                            step_number=step_number, duration=duration).first()

    if step_exists:
        return make_response(jsonify({'error': 'Cette étape existe déja !'}), 409)

    new_step = RehabilitationProgramStep(
        name=name,
        duration=duration,
        step_number=step_number,
        rehabilitation_program_id=rehabilitation_program_id
    )

    db.session.add(new_step)
    db.session.commit()

    return make_response(jsonify({'message': 'Cette étape du programme a été créée avec succès !'}), 200)
