from google.cloud.sql.connector import Connector
from sqlmodel import create_engine, Session, SQLModel
import os

def get_database():
    if os.environ.get("DB_ENGINE","CLOUD_SQL_PSQL") == "CLOUD_SQL_PSQL": 
        return GoogleCloudPostgreSQL()
    
    if os.environ.get("DB_ENGINE","CLOUD_SQL_PSQL") == "PSQL":
        return PostgreSQL()
    
    return None

class AbstractDatabase():
    
    def __init__(self):
        pass
    
    def create_db_and_tables(self):
        SQLModel.metadata.create_all(self.engine)

class PostgreSQL(AbstractDatabase):
    
    def __init__(self):
        db_password = os.environ["DB_PASSWORD"]
        db_host = os.environ["DB_HOST"]
        db_port = os.environ["DB_PORT"]
        db_username = os.environ["DB_USERNAME"]
        db_name = os.environ["DB_NAME"]
        db_url = f"postgresql+psycopg://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
        connect_args = {}
        self.engine = create_engine(db_url, connect_args=connect_args)
    

class GoogleCloudPostgreSQL(AbstractDatabase):
    
    def get_connection(self):
        db_password = os.environ["DB_PASSWORD"]
        db_host = os.environ["DB_HOST"]
        db_port = os.environ["DB_PORT"]
        db_username = os.environ["DB_USERNAME"]
        db_name = os.environ["DB_NAME"]
        return self.connector.connect(
            db_host,
            "pg8000",
            user=db_username,
            password=db_password,
            db=db_name
        )
    
    def __init__(self):
        
        self.connector = Connector()
        
        self.engine = create_engine(
            "postgresql+pg8000://",
            creator=self.get_connection,
            echo=True
        )
        
        
    