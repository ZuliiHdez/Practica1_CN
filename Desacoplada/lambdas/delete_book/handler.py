import json
from app.db.factory import DatabaseFactory
import psycopg2

def lambda_handler(event, context):
    try:
        db = DatabaseFactory.create()
        
        if event.get('httpMethod') != 'DELETE':
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
        
        deleted = db.delete_book(book_id)
        
        if deleted:
            return {
                'statusCode': 204,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,x-api-key',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': ''
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