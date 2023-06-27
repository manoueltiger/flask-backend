from app import app, db
from app.models import RehabilitationProgram, RehabilitationProgramStep, Session, Exercise

@app.route("/api/mobile/get_rehab_videos", methods=['GET'])
def get_rehab_videos(session_id):
    session = Session.query.order_by(Session.session_id.desc()).first()

    #récupérer le programme de rééducaiton de la dernière session :
    rehab_program = RehabilitationProgram.query.get(session.rehabilitation_program_id)

    #récupérer l'étape actuelle du programme :
    current_step = session.current_step

    #récupérer les vidéos sous forme de tableau de l'étape actuelle:

    rehab_videos = RehabilitationProgramStep.query.filter_by(rehabilitation_program_id=rehab_program.id,
                                                             step_number = current_step).first().exercises

    #retourner les vidéos sous forme d'un objet JSON :
