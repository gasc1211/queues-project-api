import os
import requests
import json
import logging
import traceback
import random

from dotenv import load_dotenv
from fastapi import HTTPException

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

from azure.storage.queue import QueueClient, BinaryBase64DecodePolicy, BinaryBase64EncodePolicy

from server.models.UserSignup import UserSignup
from server.models.UserLogin import UserLogin
from server.models.EmailActivation import EmailActivation
from server.models.UserActivation import UserActivation

from server.utils.database import fetch_query_as_json
from server.utils.tokens import create_jwt_token

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar la app de Firebase Admin
cred = credentials.Certificate("firebase-config.json")
firebase_admin.initialize_app(cred)

load_dotenv()

azure_sa_connection = os.getenv('AZURE_SA_CONN')
queue_name = os.getenv('QUEUE_NAME')

queue_client = QueueClient.from_connection_string(azure_sa_connection, queue_name)
queue_client.message_decode_policy = BinaryBase64DecodePolicy()
queue_client.message_encode_policy = BinaryBase64EncodePolicy()

async def insert_message_on_queue(message: str):
    message_bytes = message.encode('utf-8')
    queue_client.send_message(
        queue_client.message_encode_policy.encode(message_bytes)
    )


async def register_user_firebase(user: UserSignup):
    user_record = {}
    try:
        # Crear usuario en Firebase Authentication
        user_record = firebase_auth.create_user(
            email=user.email,
            password=user.password
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail=f"Error al registrar usuario: {e}"
        )

    query = f" EXEC [acc].[InsertUser] @email = '{user.email}', @first_name = '{user.first_name}', @last_name = '{user.last_name}'"
    
    try:
        result_json = await fetch_query_as_json(query, is_procedure=True)
        result = json.loads(result_json)

        await insert_message_on_queue(user.email)

        return result

    except Exception as e:
        firebase_auth.delete_user(user_record.uid)
        raise HTTPException(status_code=500, detail=str(e))


async def login_user_firebase(user: UserLogin):
    try:
        # Autenticar usuario con Firebase Authentication usando la API REST
        api_key = os.getenv("FIREBASE_API_KEY")  # Reemplaza esto con tu apiKey de Firebase
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {
            "email": user.email,
            "password": user.password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        response_data = response.json()

        if "error" in response_data:
            raise HTTPException(
                status_code=400,
                detail=f"Error authenticating user: {response_data['error']['message']}"
            )

        query = f"""SELECT email, first_name, last_name, is_verified 
                    FROM acc.users 
                    WHERE email = '{ user.email }'
                    """

        try:
            result_json = await fetch_query_as_json(query)
            result_dict = json.loads(result_json)
            return {
                "message": "User authenticated succesfully",
                "idToken": create_jwt_token(
                    result_dict[0]["first_name"],
                    result_dict[0]["last_name"],
                    user.email,
                    result_dict[0]["is_verified"]
                )
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        error_detail = {
            "type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(
            status_code=400,
            detail=f"Error at user login: {error_detail}"
        )


async def generate_activation_code(email: EmailActivation):

    code = random.randint(100000, 999999)
    query = f"EXEC [acc].[GenerateActivationCode] @email = '{email.email}', @verification_code = {code}"
    
    try:
        result_json = await fetch_query_as_json(query, is_procedure=True)
        # result = json.loads(result_json)[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "Activation code generated succesfully",
        "auth_code": code
    }
    
async def activate_user(user: UserActivation):

    query = f" SELECT verification_code FROM acc.users WHERE email='{user.email}'"
    
    try: 
        results_json = await fetch_query_as_json(query)
        results = json.loads(results_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    if results[0]["verification_code"] == user.auth_code:
        try: 
            procedure_query = f"EXEC acc.ActivateAccount @email='{user.email}'"
            results_json = await fetch_query_as_json(query)
            results = json.loads(results_json)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    pass