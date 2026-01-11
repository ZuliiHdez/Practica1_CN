from flask import Flask, request, jsonify
from pydantic import ValidationError
import psycopg2
from botocore.exceptions import ClientError
from models.book import Book
from db.factory import DatabaseFactory
import os
import time 
import sys  

app = Flask(__name__)

_db_instance = None

def get_db():
    global _db_instance
    if _db_instance is None:
        print("Inicializando base de datos...", file=sys.stderr)
        try:
            _db_instance = DatabaseFactory.create()
            print("Base de datos inicializada exitosamente", file=sys.stderr)
        except Exception as e:
            print(f"Error inicializando DB: {e}", file=sys.stderr)
            raise
    return _db_instance

@app.before_request
def before_request():
    print(f"[{time.time()}] {request.method} {request.path}", file=sys.stderr)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,x-api-key'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

@app.route('/books', methods=['OPTIONS'])
def options_books():
    return jsonify({'status': 'ok'}), 200

@app.route('/books/<book_id>', methods=['OPTIONS'])
def options_book(book_id):
    return jsonify({'status': 'ok'}), 200

@app.route('/books', methods=['POST'])
def create_book():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos JSON'}), 400
            
        book = Book(**data)
        created = get_db().create_book(book)
        return jsonify(created.model_dump()), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
    except psycopg2.IntegrityError as e:
        return jsonify({'error': 'Database integrity error', 'details': str(e)}), 409
    except psycopg2.OperationalError as e:
        return jsonify({'error': 'Database connection error', 'details': str(e)}), 503
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/books', methods=['GET'])
def get_all_books():
    try:
        books = get_db().get_all_books()
        return jsonify([b.model_dump() for b in books]), 200
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    try:
        book = get_db().get_book(book_id)
        if book:
            return jsonify(book.model_dump()), 200
        return jsonify({'error': 'Book not found'}), 404
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos JSON'}), 400

        data.pop('book_id', None)
        data.pop('created_at', None)
        
        book = Book(**data)
        updated = get_db().update_book(book_id, book)
        if updated:
            return jsonify(updated.model_dump()), 200
        return jsonify({'error': 'Book not found'}), 404
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        if get_db().delete_book(book_id):
            return '', 204
        return jsonify({'error': 'Book not found'}), 404
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    try:
        print("Health check iniciado", file=sys.stderr)
        
        response_data = {
            'status': 'healthy',
            'timestamp': time.time(),
            'app': 'running'
        }
        
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASS'),
                database=os.getenv('DB_NAME'),
                connect_timeout=2
            )
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            conn.close()
            response_data['database'] = 'connected'
            print("Health check: DB conectada", file=sys.stderr)
            
        except Exception as db_error:
            response_data['database'] = 'disconnected'
            response_data['db_error'] = str(db_error)
            print(f"Health check: DB error - {db_error}", file=sys.stderr)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Health check ERROR: {e}", file=sys.stderr)
        return jsonify({
            'status': 'unhealthy',
            'timestamp': time.time(),
            'error': str(e)
        }), 503

if __name__ == '__main__':
    print("Iniciando aplicación Flask Book Manager...", file=sys.stderr)
    print(f"DB_HOST: {os.getenv('DB_HOST')}", file=sys.stderr)
    print(f"DB_NAME: {os.getenv('DB_NAME')}", file=sys.stderr)
    print(f"DB_USER: {os.getenv('DB_USER')}", file=sys.stderr)
    app.run(host='0.0.0.0', port=8080, debug=True)