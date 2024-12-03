from functools import wraps
import json
import random
from http.client import HTTPException
from datetime import datetime

from queues_project_api.models.EmailActivation import EmailActivation
from queues_project_api.models.UserActivation import UserActivation
from queues_project_api.utils.database import fetch_query_as_json

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
            results_json = await fetch_query_as_json(procedure_query)
            results = json.loads(results_json)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    pass

def expire_user_code(email: str):
    
    query = f"UPDATE "
    
    pass
  
def validate_verification_code(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        
        email = kwargs.get('email')
        verification_code = kwargs.get('verification_code')
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not found")
        
        if not verification_code:
            raise HTTPException(status_code=400, detail="Account verification code not found")
        
        query = f"SELECT code_issued_at, verification_code FROM acc.users WHERE email = '{email}'"
    
    return wrapper
