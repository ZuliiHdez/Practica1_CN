CREATE TABLE books (
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
