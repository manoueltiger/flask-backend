from app import app, db
from flask import request, make_response, jsonify
from app.models import RehabilitationProgram, RehabilitationProgramStep, Session, ExerciseSession, Exercise, \
    ProgramExercise, MedicalCare
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_cors import cross_origin


@app.route('/api/create_exercise', methods=['POST'])
@cross_origin()
def create_exercise():
    title = request.json.get('title', None)
    description = request.json.get('description', None)
    video_link = request.json.get('video_link', None)
    duration = request.json.get('duration', None)
    iteration = request.json.get('iteration', None)

    exercise_exists = Exercise.query.filter_by(title=title, video_link=video_link, duration=duration).first()

    if exercise_exists:
        return make_response(jsonify({'error': 'Cet exercice existe déja !'}), 409)

    new_exercice = Exercise(title=title, description=description, video_link=video_link, duration=duration, iteration=iteration)
    db.session.add(new_exercice)
    db.session.commit()

    return make_response(jsonify({'message': 'Nouvel exercice ajouté avec succès !'}), 200)

@app.route('/api/get_all_exercises', methods=['GET'])
@cross_origin()
def get_all_exercises():
    exercises = Exercise.query.all()
    results=[]

    for exercise in exercises:
        result= {
            'id': exercise.id,
            'title': exercise.title,
            'description': exercise.description,
            'video_link': exercise.video_link,
            'duration': exercise.duration,
            'iteration': exercise.iteration
        }
        results.append(result)

    return jsonify(results)

@app.route('/api/associate_steps_exercices', methods=['POST'])
@cross_origin()
def associate_steps_and_exercices():
    program_step_id = request.json.get('program_step_id', None)
    exercise_id = request.json.get('exercise_id', None)

    program_exercise_exists = ProgramExercise.query.filter_by(program_step_id=program_step_id, exercise_id=exercise_id).first()

    if program_exercise_exists:
        return make_response(jsonify({'error': 'Cette association esite déja'}), 409)

    new_association = ProgramExercise(program_step_id=program_step_id, exercise_id=exercise_id)

    db.session.add(new_association)
    db.session.commit()

    return make_response(jsonify({'message': 'Exercice associé à une étape de programme avec succès'}), 200)


@app.route("/api/mobile/get_rehab_videos", methods=['GET'])
@cross_origin()
def get_rehab_videos(session_id):
    session = Session.query.order_by(Session.session_id.desc()).first()

    #récupérer le programme de rééducaiton de la dernière session :
    rehab_program = RehabilitationProgram.query.get(session.rehabilitation_program_id)

    #récupérer l'étape actuelle du programme :
    current_step = session.current_step

    #récupérer les vidéos sous forme de tableau de l'étape actuelle:

    rehab_videos = RehabilitationProgramStep.query.filter_by(rehabilitation_program_id=rehab_program.id,
                                                             step_number=current_step).first().exercises

    #retourner les vidéos sous forme d'un objet JSON :
    videos_list = []

    for video in rehab_videos:
        rehab_video = {
            'id': video.id,
            'title': video.title,
            'description': video.description,
            'video_link': video.video_link,
            'duration': video.duration,
            'iteration': video.iteration
        }
        videos_list.append(rehab_video)

    return jsonify(videos_list)

@app.route('/api/mobile/get_video/<int:medical_care_id>/<int:current_step>', methods=['GET'])
def get_videos(medical_care_id, current_step):

    medical_care = MedicalCare.query.get(medical_care_id)

    #récupérer le programme en fonction d'une prise en charge spécifique
    rehab_program = RehabilitationProgram.query.filter_by(medical_care_id= medical_care.id).first()

    #récupérer la liste des vidéos en fonction du programme et de l'étape dans le programme
    rehab_videos = RehabilitationProgramStep.query.filter_by(rehabilitation_program_id=rehab_program.id,
                                                             step_number = current_step).first().exercises

    #retourner les vidéos sous forme d'un objet JSON :
    videos_list = []

    for video in rehab_videos:
        rehab_video = {
            'id': video.id,
            'title': video.title,
            'description': video.description,
            'video_link': video.video_link,
            'duration': video.duration,
            'iteration': video.iteration
        }
        videos_list.append(rehab_video)

    return jsonify(videos_list)

@app.route("/api/mobile/create_first_exercice_session", methods=['POST'])
def create_first_exercice_session():
    session_id = request.json.get('session_id', None)
    #récupérer la session et le programme de rééducation lié au session_id
    session = Session.query.get(session_id)
    rehab_program = RehabilitationProgram.query.get(session.rehabilitation_program_id)

    #récupérer la liste des exercices de la première étap du programme de rééducation
    rehab_videos = RehabilitationProgramStep.query.filter_by(rehabilitation_program_id=rehab_program.id, step_number=1)\
        .first().exercises

    #créer une ligne en base  pour un compteur de lecture de vidéos pour exercice du programme
    for exercise in rehab_videos:
        new_exercise_session = ExerciseSession(session_id=session_id, exercise_id=exercise.id, count=0)
        db.session.add(new_exercise_session)

    db.session.commit()

    return make_response(jsonify({'message': 'ExerciseSession mis à jour avec succès'}), 200)


@app.route("/api/mobile/create_exercice_after_new_session", methods=['POST'])
def create_new_exercice_session():
    session_id = request.json.get('session_id',None)
    session = Session.query.get(session_id)
    rehab_exercises = RehabilitationProgram.query.filter_by(session.rehabilitation_program_id,
                                                          step_number=session.current_step).first().exercises

    for exercise in rehab_exercises:
        new_exercise_session = ExerciseSession(session_id=session_id, exercise_id=exercise.id, count=0)
        db.session.add(new_exercise_session)

    db.session.commit()

    return make_response(jsonify({'message': 'ExerciseSession mis à jour avec succès'}), 200)

@app.route("/api/mobile/exercises/<exercise_id>/complete", methods=["POST"])
@cross_origin()
def complete_exercise(exercise_id):
    session_id = request.json.get('session_id', None)

    #récupérer le compteur d'un exercice pour une session donnée
    exercise_count = ExerciseSession.query.filter_by(session_id=session_id, exercise_id=exercise_id).first()

    if exercise_count is None:
        return make_response(jsonify({'error': 'la variable exerciseSession est introuvable'}), 404)

    #incrémenter le compteur des exercices
    exercise_count.count += 1
    db.session.commit()

    return make_response(jsonify({'message': "Compteur de lecture d'exercice incrémenté avec succès"}), 200)

@app.route('/api/mobile/test', methods=['GET'])
def test():
    return jsonify({'message': 'ceci est un test'})