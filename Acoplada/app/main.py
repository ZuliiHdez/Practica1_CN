from flask import Flask, request, jsonify, send_from_directory
from pydantic import ValidationError
import psycopg2
from botocore.exceptions import ClientError
from models.book import Book
from db.factory import DatabaseFactory
import os

app = Flask(__name__, static_folder=os.path.dirname(os.path.abspath(__file__)))

try:
    db = DatabaseFactory.create()
except ValueError as e:
    raise RuntimeError(f"Error initializing DB: {e}") from e

@app.route('/')
def serve_frontend():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'frontend.html')

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin', '*')
    
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, x-api-key, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response

@app.route('/books', methods=['OPTIONS'])
def options_books():
    response = jsonify({'status': 'ok'})
    return response

@app.route('/books/<book_id>', methods=['OPTIONS'])
def options_book(book_id):
    response = jsonify({'status': 'ok'})
    return response

@app.route('/books', methods=['POST'])
def create_book():
    try:
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'})
            
        data = request.get_json()
        book = Book(**data)
        created = db.create_book(book)
        return jsonify(created.model_dump()), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
    except psycopg2.IntegrityError as e:
        return jsonify({'error': 'Database integrity error', 'details': str(e)}), 409
    except psycopg2.OperationalError as e:
        return jsonify({'error': 'Database connection error', 'details': str(e)}), 503
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except ClientError as e:
        return jsonify({'error': 'AWS error', 'details': e.response['Error']['Message']}), 500

@app.route('/books', methods=['GET'])
def get_all_books():
    try:
        books = db.get_all_books()
        return jsonify([b.model_dump() for b in books]), 200
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    try:
        book = db.get_book(book_id)
        if book:
            return jsonify(book.model_dump()), 200
        return jsonify({'error': 'Book not found'}), 404
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        data = request.get_json()
        data.pop('book_id', None)
        data.pop('created_at', None)
        book = Book(**data)
        updated = db.update_book(book_id, book)
        if updated:
            return jsonify(updated.model_dump()), 200
        return jsonify({'error': 'Book not found'}), 404
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        if db.delete_book(book_id):
            return '', 204
        return jsonify({'error': 'Book not found'}), 404
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)