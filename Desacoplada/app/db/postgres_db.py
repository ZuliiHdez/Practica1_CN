import psycopg2
import psycopg2.extras
from typing import List, Optional
from app.db.db import Database
from app.models.book import Book
import os
import json
from datetime import datetime


class PostgresDatabase(Database):
    
    def __init__(self):
        self.connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
        self.connection.autocommit = True
        self.initialize()
    
    def initialize(self):
        """Crea la tabla books si no existe."""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    book_id        VARCHAR(36) PRIMARY KEY,
                    title          VARCHAR(255) NOT NULL,
                    author         VARCHAR(255) NOT NULL,
                    genre          VARCHAR(100),
                    year           INTEGER CHECK (year >= 0),
                    status         VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'borrowed', 'reserved', 'lost')),
                    rating         VARCHAR(10) DEFAULT 'medium' CHECK (rating IN ('low', 'medium', 'high', 'excellent')),
                    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags           JSONB
                );
            """)


    def _normalize_tags(self, value):
        """Normaliza el campo tags para garantizar siempre una lista."""
        if value is None:
            return []
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return []
        return value  


    def create_book(self, book: Book) -> Book:
        with self.connection.cursor() as cursor:
            sql = """
                INSERT INTO books 
                (book_id, title, author, genre, year, status, rating, created_at, updated_at, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                book.book_id,
                book.title,
                book.author,
                book.genre,
                book.year,
                book.status,
                book.rating,
                book.created_at,
                book.updated_at,
                json.dumps(book.tags)
            ))
        return book

    def get_book(self, book_id: str) -> Optional[Book]:
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            sql = "SELECT * FROM books WHERE book_id = %s"
            cursor.execute(sql, (book_id,))
            result = cursor.fetchone()

            if result:
                result = dict(result)
                result["created_at"] = result["created_at"].isoformat() if result["created_at"] else None
                result["updated_at"] = result["updated_at"].isoformat() if result["updated_at"] else None
                result["tags"] = self._normalize_tags(result.get("tags"))
                return Book(**result)
        return None

    def get_all_books(self) -> List[Book]:
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            sql = "SELECT * FROM books ORDER BY created_at DESC"
            cursor.execute(sql)
            results = cursor.fetchall()

            books = []
            for row in results:
                row = dict(row)
                row["created_at"] = row["created_at"].isoformat() if row["created_at"] else None
                row["updated_at"] = row["updated_at"].isoformat() if row["updated_at"] else None
                row["tags"] = self._normalize_tags(row.get("tags"))
                books.append(Book(**row))
            return books

    def update_book(self, book_id: str, book: Book) -> Optional[Book]:
        book.updated_at = datetime.utcnow()
        with self.connection.cursor() as cursor:
            sql = """
                UPDATE books 
                SET title=%s, author=%s, genre=%s, year=%s, status=%s,
                    rating=%s, updated_at=%s, tags=%s
                WHERE book_id=%s
            """
            cursor.execute(sql, (
                book.title, book.author, book.genre, book.year,
                book.status, book.rating, book.updated_at,
                json.dumps(book.tags), book_id
            ))
            if cursor.rowcount > 0:
                return self.get_book(book_id)
        return None

    def delete_book(self, book_id: str) -> bool:
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM books WHERE book_id = %s"
            cursor.execute(sql, (book_id,))
            return cursor.rowcount > 0