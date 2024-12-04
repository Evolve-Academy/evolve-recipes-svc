from google.cloud.sql.connector import Connector
from sqlmodel import create_engine
import os

db_password = os.environ["DB_PASSWORD"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_username = os.environ["DB_USERNAME"]
db_name = os.environ["DB_NAME"]

# create connection pool with 'creator' argument to our connection object function
def get_engine_cloud_sql():
    # initialize Connector object
    connector = Connector()
    return create_engine(
        "postgresql+pg8000://",
        creator=connector.connect(
            db_host,
            "pg8000",
            user=db_username,
            password=db_password,
            db=db_name
        ),
    )

def get_engine_postgres():
    db_url = f"postgresql+psycopg://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
    connect_args = { }
    return create_engine(db_url, connect_args=connect_args)

def get_engine():
    return get_engine_postgres() if os.environ.get("DB_ENGINE_CLOUD_SQL","0") == "0" else get_engine_cloud_sql()