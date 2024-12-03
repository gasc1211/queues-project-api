import re

from typing import Optional 
from pydantic import BaseModel, field_validator
from server.utils.globalf import validate_sql_injection

class UserSignup(BaseModel):
  
  first_name: str
  last_name: str
  email: str
  password: str
  
  @field_validator('password')
  def password_validation(cls, value):
    if (len(value) < 8):
      raise ValueError("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', value):
      raise ValueError("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', value):
      raise ValueError("Password must contain at least one lowercase letter")
    
    if not re.search(r'[\W_]', value):
      raise ValueError("Password must contain at least one special character")
    
    if re.search(r'(012|123|234|345|456|567|678|789|890)', value):
      raise ValueError("Password must not contain a sequence of numbers")
    
    return value
  @field_validator('first_name')
  def name_validator(cls, value):
    if validate_sql_injection(value):
      raise ValueError("Invalid name")
    
    return value