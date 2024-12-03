import re
from pydantic import BaseModel, field_validator

class UserActivation(BaseModel):
    email: str
    auth_code: str

    @field_validator('email')
    def email_validation(cls, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError('Invalid email address')

        
        return value
   
    @field_validator('auth_code')
    def auth_code_validation(cls, value):
        if value < 100000 or value > 999999:
            raise ValueError('Invalid verification code')
        
        return value