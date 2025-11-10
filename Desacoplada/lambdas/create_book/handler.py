import json
from pydantic import ValidationError
import psycopg2
from botocore.exceptions import ClientError

from app.models.book import Book, BookCreate
from app.db.factory import DatabaseFactory

db = DatabaseFactory.create()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,x-api-key",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}

def build_response(status_code: int, body: dict):
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body, default=str)
    }

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        payload = BookCreate(**body)
        book = Book(**payload.model_dump()) 
        created = db.create_book(book)
        return build_response(201, created.model_dump())

    except ValidationError as e:
        return build_response(400, {"error": "Validation error", "details": e.errors()})
    except psycopg2.IntegrityError as e:
        return build_response(409, {"error": "Database integrity error", "details": str(e)})
    except psycopg2.OperationalError as e:
        return build_response(503, {"error": "Database connection error", "details": str(e)})
    except psycopg2.Error as e:
        return build_response(500, {"error": "Database error", "details": str(e)})
    except ClientError as e:
        return build_response(500, {"error": "AWS error", "details": e.response.get("Error", {}).get("Message")})
