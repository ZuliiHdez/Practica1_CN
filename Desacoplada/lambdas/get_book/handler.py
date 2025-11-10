import json
from app.db.factory import DatabaseFactory
from app.models.book import Book
import psycopg2

def lambda_handler(event, context):
    try:
        db = DatabaseFactory.create()

        if event.get('httpMethod') != 'GET':
            return {
                'statusCode': 405,
                'body': json.dumps({'error': 'Method not allowed'})
            }

        book_id = event.get('pathParameters', {}).get('id')
        if not book_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Book ID is required'})
            }

        book = db.get_book(book_id)

        if book and isinstance(book, Book):
            book_serialized = {
                **book.model_dump(),
                'created_at': book.created_at.isoformat() if book.created_at else None,
                'updated_at': book.updated_at.isoformat() if book.updated_at else None
            }
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,x-api-key',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps(book_serialized, default=str)  
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Book not found'})
            }

    except psycopg2.OperationalError as e:
        return {
            'statusCode': 503,
            'body': json.dumps({'error': 'Database connection error', 'details': str(e)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }