import sqlalchemy

DB_PATH = './DB/store_main.db'

def setup_database():
    engine = sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")
    return engine