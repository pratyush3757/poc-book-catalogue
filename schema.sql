DROP TABLE IF EXISTS books;

CREATE TABLE books (
    isbn INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    page_count INTEGER NOT NULL,
    maturity_rating TEXT,
    thumbnail_url TEXT
);
