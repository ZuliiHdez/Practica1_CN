import json
import logging
from datetime import datetime
from app.db.factory import DatabaseFactory
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    logger.info("Inicializando la base de datos...")
    db = DatabaseFactory.create()
    logger.info("Base de datos inicializada correctamente")
except Exception as e:
    logger.exception("Error al crear la instancia de la base de datos")
    db = None  

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,x-api-key",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}

def build_response(status_code: int, body):
    """Construye respuesta JSON con cabeceras CORS y manejo de datetime"""
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body, default=str)
    }

def normalize_book(book_dict: dict) -> dict:
    """Normaliza tags y fechas de un libro"""
    tags = book_dict.get("tags")
    if isinstance(tags, str):
        try:
            book_dict["tags"] = json.loads(tags)
        except json.JSONDecodeError:
            book_dict["tags"] = []
    elif tags is None:
        book_dict["tags"] = []

    for date_field in ["created_at", "updated_at"]:
        val = book_dict.get(date_field)
        if isinstance(val, datetime):
            book_dict[date_field] = val.isoformat()
        elif val is None:
            book_dict[date_field] = None

    return book_dict

def lambda_handler(event, context):
    """GET /books → obtiene todos los libros"""
    if db is None:
        logger.error("La base de datos no está disponible")
        return build_response(500, {"error": "Database not initialized"})

    logger.info("Evento recibido: %s", json.dumps(event))
    try:
        books = db.get_all_books()
        logger.info("Se recuperaron %d libros", len(books))

        serialized_books = [normalize_book(b.model_dump()) for b in books]

        return build_response(200, serialized_books)

    except psycopg2.Error as db_err:
        logger.exception("Error en la base de datos")
        return build_response(500, {"error": "Database error", "details": str(db_err)})

    except Exception as e:
        logger.exception("Error inesperado en Lambda")
        return build_response(500, {"error": "Unexpected error", "details": str(e)})
