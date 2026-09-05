import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv("DATABASE_URL")

try:
    with psycopg.connect(connection_string) as connection:
            with connection.cursor() as cursor:
                  
    
                connection.close()
except Exception as reason:
    print("connection failed")
    print(reason)