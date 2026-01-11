import os
from typing import Dict, Type
from .db import Database
from .postgres_db import PostgresDatabase

class DatabaseFactory:
    
    _databases: Dict[str, Type[Database]] = {
        'postgres': PostgresDatabase,
    }
    
    @classmethod
    def create(cls, db_type: str = None) -> Database:
        if db_type is None:
            db_type = os.getenv('DB_TYPE', 'postgres')
        
        db_type = db_type.lower()
        
        database_class = cls._databases.get(db_type)
        
        if database_class is None:
            available = ', '.join(cls._databases.keys())
            raise ValueError(
                f"DB_TYPE '{db_type}' no válido. "
                f"Opciones disponibles: {available}"
            )
        return database_class()
    
    @classmethod
    def get_available_databases(cls) -> list:
        return list(cls._databases.keys())