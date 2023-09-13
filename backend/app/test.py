from flask import request, jsonify, make_response
from app import app
from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection
from flask_cors import cross_origin
import random

@app.route('/api/test/create_user', method=['POST'])
@cross_origin()
def create_keycloak_user():

    keycloak_config = KeycloakOpenIDConnection(
        server_url="http://localhost:8080/",
        realm_name="test",
        client_id="flask-api",
        client_secret_key="KvDckxjAY7mYaWmOke8hASalvCpMx8uq",
        verify=True
    )

    keycloak_admin = KeycloakAdmin(connection=keycloak_config)

    token = keycloak_admin.token(grand_type='client_credentials')

    email = request.json('email', None)
    username = request.json('username', None)
    first_name = request.json('firstName', None)
    last_name = request.json('lastname', None)

    password = ''.join(random.choices('0123456789', k=8))

    try :
        #créer un nouvel utilisateur Keycloak
        new_user = keycloak_admin.create_user({
            "email": email,
            "username": username,
            "enabled": True,
            "firstName": first_name,
            "lastname": last_name,
            "attributes": {
                "role": "patient"
            },
            "credentials": [{
                "value": "password",
                "type": password,
                "temporary": True
            }]
        }, token=token, exist_ok=False)
    except Exception as e:
        print(e)

    return make_response(jsonify({"message": "Utilisateur créé avec succès"}), 201)


