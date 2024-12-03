from dotenv import load_dotenv
import os
import pyodbc # type: ignore
import logging
import json

load_dotenv()

# Configure console logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection environment variables
driver = os.getenv('SQL_DRIVER')
server = os.getenv('SQL_SERVER')
database = os.getenv('SQL_DATABASE')
username = os.getenv('SQL_USERNAME')
password = os.getenv('SQL_PASSWORD')

# Construct connection string
connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

async def get_db_connection():
    """ Get database connection """
    try:
        logger.info(f"Attempting connection to database: {connection_string}")
        conn = pyodbc.connect(connection_string, timeout=10)
        logger.info("Succesful connection to database")
        return conn
    except pyodbc.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise Exception(f"Database connection error: {str(e)}")

async def fetch_query_as_json(query, is_procedure=False):
    """ Fetch query results and format as json"""
    conn = await get_db_connection()
    cursor = conn.cursor()
    logger.info(f"Executing query: {query}")
    try:
        cursor.execute(query)

        columns = [column[0] for column in cursor.description]
        results = []
        logger.info(f"Columns: {columns}")
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        if is_procedure:
            conn.commit()
            
        return json.dumps(results)

    except pyodbc.Error as e:
        raise Exception(f"Error executing the requested query: {str(e)}")
    finally:
        cursor.close()
        conn.close()