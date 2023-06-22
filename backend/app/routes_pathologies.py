from flask import request, jsonify, make_response
from app import app, db
from app.models import User, Patient, Speciality, LocationPathology, Pathology
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