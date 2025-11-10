import json
from app.db.factory import DatabaseFactory
from app.models.book import Book
from pydantic import ValidationError
import psycopg2

def lambda_handler(event, context):
    try:
        db = DatabaseFactory.create()
        
        if event.get('httpMethod') != 'PUT':
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
        
        body = json.loads(event.get('body', '{}'))
        body.pop('book_id', None)
        body.pop('created_at', None)
        body.pop('updated_at', None)
        
        book = Book(**body)
        updated = db.update_book(book_id, book)

        if isinstance(updated, list) and len(updated) == 1:
            updated = updated[0]
        
        if updated:
            updated_serialized = {
                **updated.model_dump(),
                'created_at': updated.created_at.isoformat() if updated.created_at else None,
                'updated_at': updated.updated_at.isoformat() if updated.updated_at else None
            }
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,x-api-key',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps(updated_serialized, default=str)  
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Book not found'})
            }
            
    except ValidationError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Validation error', 'details': e.errors()})
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