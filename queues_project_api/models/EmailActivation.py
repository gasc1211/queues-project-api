import re
from pydantic import BaseModel, field_validator


class EmailActivation(BaseModel):
    email: str

    @field_validator('email')
    def email_validation(cls, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError('Invalid email address')

        return value