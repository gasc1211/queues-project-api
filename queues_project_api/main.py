import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from queues_project_api.utils.tokens import validate, validate_func

from queues_project_api.models.UserLogin import UserLogin
from queues_project_api.models.UserSignup import UserSignup
from queues_project_api.controllers.firebase import register_user_firebase, login_user_firebase

from queues_project_api.models.EmailActivation import EmailActivation
from queues_project_api.models.UserActivation import UserActivation
from queues_project_api.controllers.verification import activate_user, generate_activation_code, validate_verification_code, expire_user_code, validate_account

app = FastAPI()

load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return "Hello from queues-project API!"

@app.post("/signup")
async def signup(user: UserSignup):
  """ Signup for the application """
  return await register_user_firebase(user)

@app.post("/signin")
async def signin(request: Request, user: UserLogin):
  """ Login into the application"""
  return await login_user_firebase(user)

@app.get("/user")
@validate
async def user(request: Request, response: Response):
    """ Get user data from jwt token metadata"""
    response.headers["Cache-Control"] = "no-cache";
    return {
        "first_name": request.state.first_name,
        "last_name": request.state.last_name,
        "email": request.state.email,
        "created_at": request.state.created_at
    }

@app.post("/user/{email}/verification_code")
@validate_func
# @validate_account
async def generate_code(request: Request, email: str):
    """ Generate user account activation code"""
    e = EmailActivation(email=email)
    return await generate_activation_code(e)

@app.put("/user/verification")
@validate_account
@validate_verification_code
async def verificate_code(user: UserActivation):
    """ Verify auth code sent to user through email"""
    return await activate_user(user)

@app.put("/user/{email}/expire_codes")
async def expire_code(email: str):
    return expire_user_code(email)

if __name__=="__main__":
    __host__ = os.getenv("HOST")
    __port__ = int(os.getenv("PORT"))
    
    uvicorn.run("queues_project_api.main:app", host=__host__, port=__port__, reload=True)