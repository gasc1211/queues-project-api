""" Queue Function Backend API """

import uvicorn
from dotenv import load_dotenv 
import os

load_dotenv()

__host__ = os.getenv("HOST")
__port__ = int(os.getenv("PORT"))

def dev():
  """ Launched with 'poetry run dev' at root level """
  uvicorn.run("queues_project_api.main:app", host=__host__, port=__port__, reload=True)
