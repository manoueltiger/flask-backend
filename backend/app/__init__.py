from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail


app = Flask(__name__)
app.config.from_object(Config)
app.config['JWT_SECRET_KEY'] = 'votre_clé_secrète_ici'
app.config['CORS_HEADERS'] = 'Content-Type'


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'emmanuel.tigier@gmail.com'
app.config['MAIL_PASSWORD'] = 'lafpdfvbnhmnlcsc'

mail = Mail(app)
db = SQLAlchemy(app)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
migrate = Migrate(app, db)
jwt = JWTManager(app)

from app import routes, routes_patient, routes_pathologies, models
