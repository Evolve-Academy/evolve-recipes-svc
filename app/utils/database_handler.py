from google.cloud.sql.connector import Connector
from sqlmodel import create_engine, Session, SQLModel
import os

class Database():
    
    def __init__(self):
        
        self.db_password = os.environ["DB_PASSWORD"]
        self.db_host = os.environ["DB_HOST"]
        self.db_port = os.environ["DB_PORT"]
        self.db_username = os.environ["DB_USERNAME"]
        self.db_name = os.environ["DB_NAME"]
        # get engine
        self.engine = self.get_engine_postgres() if os.environ.get("DB_ENGINE_CLOUD_SQL","0") == "0" else self.get_engine_cloud_sql()

    # create connection pool with 'creator' argument to our connection object function
    def get_engine_cloud_sql(self):
        return create_engine(
            "postgresql+pg8000://",
            creator=Connector().connect(
                self.db_host,
                "pg8000",
                user=self.db_username,
                password=self.db_password,
                db=self.db_name
            ),
        )

    def get_engine_postgres(self):
        db_url = f"postgresql+psycopg://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        connect_args = {}
        return create_engine(db_url, connect_args=connect_args)

    def create_db_and_tables(self):
        SQLModel.metadata.create_all(self.engine)
