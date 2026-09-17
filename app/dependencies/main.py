from app.database.local import LocalDatabase


local_database = LocalDatabase()

def get_database() -> LocalDatabase:
    return local_database