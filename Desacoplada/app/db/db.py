from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.book import Book


class Database(ABC):
    
    @abstractmethod
    def initialize(self):
        pass
    
    @abstractmethod
    def create_book(self, book: Book) -> Book:
        pass
    
    @abstractmethod
    def get_book(self, book_id: str) -> Optional[Book]:
        pass
    
    @abstractmethod
    def get_all_books(self) -> List[Book]:
        pass
    
    @abstractmethod
    def update_book(self, book_id: str, book: Book) -> Optional[Book]:
        pass
    
    @abstractmethod
    def delete_book(self, book_id: str) -> bool:
        pass
