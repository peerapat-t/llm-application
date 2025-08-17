import sqlalchemy

DB_PATH = './DATABASE/main_db.db'

def setup_database():
    engine = sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")
    return engine