import requests
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

app = Flask(__name__)

GOOGLE_BOOK_API = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
DB_QUERY_BOOK_LIST = "SELECT * FROM books"

def add_book(isbn, title, author, page_count, maturity_rating, thumbnail_url):
    conn = get_db_connection()
    sqlite_insert_query = """INSERT OR REPLACE INTO books
    (isbn, title, author, page_count, maturity_rating, thumbnail_url)
    VALUES
    (?, ?, ?, ?, ?, ?)
    """
    conn.execute(sqlite_insert_query, (isbn, title, author, page_count, maturity_rating, thumbnail_url))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

def remove_book(isbn):
    conn = get_db_connection()
    sqlite_remove_query = f"""DELETE FROM books WHERE isbn={isbn}"""
    conn.execute(sqlite_remove_query)
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def call_isbn_api(isbn: str):
    response = requests.get(GOOGLE_BOOK_API + isbn)
    json_data = response.json() if response and response.status_code == 200 else None

    return json_data

def json_to_book(response):
    books = []
    for book in response['items']:
        entry = {"isbn": 0, "title": "", 
            "author": "", 
            "page_count" : 0, 
            "maturity_rating": "", 
            "thumbnail_url" : ""}
        entry["isbn"] = book["volumeInfo"]["industryIdentifiers"][0]["identifier"] #isbn_13
        entry["title"] = book["volumeInfo"]["title"]
        entry["author"] = ", ".join(book["volumeInfo"]["authors"])
        entry["page_count"] = book["volumeInfo"]["pageCount"]
        entry["maturity_rating"] = book["volumeInfo"]["maturityRating"]
        entry["thumbnail_url"] = book["volumeInfo"]["imageLinks"]["thumbnail"]
        books.append(entry)

    return books

@app.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute(DB_QUERY_BOOK_LIST).fetchall()
    return render_template('index.html', books=books)


@app.route('/search')
def search():
    query = request.args.get('search')
    res = call_isbn_api(isbn=query)
    if res['totalItems'] != 0:
        books = json_to_book(res)
        return render_template('search.html', books=books)
    return redirect(url_for('error_ops'))


@app.route('/addbook')
def addbook():
    isbn = request.args.get('isbn')
    title = request.args.get('title')
    author = request.args.get('author')
    page_count = request.args.get('page_count')
    maturity_rating = request.args.get('maturity_rating')
    thumbnail_url = request.args.get('thumbnail_url')
    if not (isbn and title and author and page_count):
        return redirect(url_for('error_ops'))
    else:
        return add_book(isbn, title, author, page_count, maturity_rating, thumbnail_url)


@app.route('/removebook')
def removebook():
    isbn = request.args.get('isbn')
    if not isbn:
        return redirect(url_for('error_ops'))
    else:
        return remove_book(isbn)

@app.route('/error')
def error_ops():
    return render_template('error.html')

