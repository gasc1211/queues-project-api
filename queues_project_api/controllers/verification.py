from functools import wraps
import json
import logging
import random
from http.client import HTTPException
from datetime import datetime, timedelta

import pytz

from queues_project_api.controllers.firebase import insert_message_on_queue
from queues_project_api.models.EmailActivation import EmailActivation
from queues_project_api.models.UserActivation import UserActivation
from queues_project_api.utils.database import fetch_query_as_json

# Configure console logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_activation_code(email: EmailActivation):

    code = random.randint(100000, 999999)
    query = f"EXEC [acc].[GenerateActivationCode] @email = '{email.email}', @verification_code = {code}"
    
    try:
        result_json = await fetch_query_as_json(query, is_procedure=True)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "Activation code generated succesfully",
        "verification_code": code
    }
    
async def activate_user(user: UserActivation):

    query = f"SELECT verification_code, code_issued_at FROM acc.users WHERE email='{user.email}'"
    
    try: 
        results_json = await fetch_query_as_json(query)
        results = json.loads(results_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    if results[0]["verification_code"] == user.verification_code:
        try: 
            procedure_query = f"EXEC acc.ActivateAccount @email='{user.email}'"
            results_json = await fetch_query_as_json(procedure_query, is_procedure=True)
            results = json.loads(results_json)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    pass

def expire_user_code(email: str):
    # TODO: Implement user verification_code expiration or invalidation
    # query = f"UPDATE "
    pass
  
def validate_verification_code(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        
        user: UserActivation = kwargs.get('user')
        
        if not user.email:
            raise HTTPException(status_code=400, detail="Email not found")
        
        if not user.verification_code:
            raise HTTPException(status_code=400, detail="Account verification code not found")
        
        # TODO: Verify code expiration
        query = f"SELECT code_issued_at, verification_code FROM acc.users WHERE email = '{user.email}'"
        
        try:
            result = await fetch_query_as_json(query)
            
            if not result:
                raise HTTPException(status_code=403, detail="Account does not exist")
            
            results = json.loads(result)
            
            # Generate a new code if expired
            if (datetime.fromisoformat(results[0]["code_issued_at"]).replace(tzinfo=pytz.timezone('UTC')) + timedelta(minutes=10)) < datetime.now(pytz.timezone('UTC')):
                await insert_message_on_queue(user.email)
                raise HTTPException(status_code=401, detail="Expired verification code")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        return await func(*args, **kwargs)
    
    return wrapper

def validate_account(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        
        email = kwargs.get("email")
        
        # TODO: Implement account existance verification
        query = f"SELECT user_id FROM acc.users WHERE email = '{email}'"
        
        try:
            result = await fetch_query_as_json(query)
            
            if not result:
                raise HTTPException(status_code=403, detail="Account does not exist")
            
            results = json.loads(result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        
        return await func(*args, **kwargs)
        
    return wrapper