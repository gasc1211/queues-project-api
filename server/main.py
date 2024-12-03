import os
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from server.models.EmailActivation import EmailActivation
from server.models.UserActivation import UserActivation
from server.utils.tokens import validate, validate_func

from .models.UserLogin import UserLogin
from .models.UserSignup import UserSignup
from .controllers.firebase import activate_user, generate_activation_code, register_user_firebase, login_user_firebase

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
  return "Hello from FastAPI!"


@app.post("/signup")
async def signup(user: UserSignup):
  """ Signup for the application """
  return await register_user_firebase(user)

@app.post("/signin")
async def signin(user: UserLogin):
  """ Login into the application"""
  return await login_user_firebase(user)

@app.get("/user")
@validate
async def user(request: Request, response: Response):
    """ Get user data from jwt token metadata"""
    response.headers["Cache-Control"] = "no-cache";
    return {
        "email": request.state.email
        , "firstname": request.state.firstname
        , "lastname": request.state.lastname
    }

@app.post("/user/{email}/auth_code")
@validate_func
async def generate_code(request: Request, email: str):
    """ Generate user account activation code"""
    e = EmailActivation(email=email)
    return await generate_activation_code(e)

@app.put("/user/verification")
async def verify_auth_code(request, email: str, auth_code: int):
    """ Verify auth code sent to user through email"""
    user = UserActivation(email=email, auth_code=auth_code)
    return activate_user(user)

if __name__=="__main__":
    __host__ = os.getenv("HOST")
    __port__ = int(os.getenv("PORT"))
    
    uvicorn.run("server.main:app", host=__host__, port=__port__, reload=True)