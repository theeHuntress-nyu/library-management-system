# Full Python source code for a Library Management System based on your 3-tier architecture

from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='templates')
DB_NAME = 'library.db'

# Initialize database if not exists
def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.executescript('''
        CREATE TABLE IF NOT EXISTS Members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            membership_date TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Librarians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Publishers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            publisher TEXT NOT NULL,
            total_copies INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            book_id INTEGER,
            loan_date TEXT NOT NULL,
            return_date TEXT,
            FOREIGN KEY (member_id) REFERENCES Members(id),
            FOREIGN KEY (book_id) REFERENCES Books(id)
        );

        CREATE TABLE IF NOT EXISTS Reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            book_id INTEGER,
            reservation_date TEXT NOT NULL,
            FOREIGN KEY (member_id) REFERENCES Members(id),
            FOREIGN KEY (book_id) REFERENCES Books(id)
        );

        CREATE TABLE IF NOT EXISTS Fines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER,
            amount REAL NOT NULL,
            paid BOOLEAN DEFAULT 0,
            FOREIGN KEY (loan_id) REFERENCES Loans(id)
        );

        CREATE VIEW IF NOT EXISTS AvailableBooks AS
        SELECT b.id, b.title, b.total_copies
        FROM Books b
        WHERE b.total_copies > 0;

        CREATE VIEW IF NOT EXISTS BookLoansReport AS
        SELECT m.name AS member_name, COUNT(l.id) AS total_loans
        FROM Members m
        JOIN Loans l ON m.id = l.member_id
        GROUP BY m.id;

        CREATE TRIGGER IF NOT EXISTS loan_book_trigger
        AFTER INSERT ON Loans
        BEGIN
            UPDATE Books SET total_copies = total_copies - 1
            WHERE id = NEW.book_id;
        END;

        CREATE TRIGGER IF NOT EXISTS return_book_trigger
        AFTER DELETE ON Loans
        BEGIN
            UPDATE Books SET total_copies = total_copies + 1
            WHERE id = OLD.book_id;
        END;
        ''')

        conn.commit()
        conn.close()

# Helper to get DB connection
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Simulated stored procedure: loan a book
def loan_book(member_id, book_id):
    conn = get_db_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    conn.execute('INSERT INTO Loans (member_id, book_id, loan_date) VALUES (?, ?, ?)', (member_id, book_id, today))
    conn.commit()
    conn.close()

# Simulated function: calculate fine
def calculate_fine(loan_date_str):
    loan_date = datetime.strptime(loan_date_str, "%Y-%m-%d")
    due_date = loan_date + timedelta(days=14)
    today = datetime.now()
    if today > due_date:
        overdue_days = (today - due_date).days
        return round(overdue_days * 0.50, 2)  # $0.50 per overdue day
    return 0.00

@app.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM Books').fetchall()
    conn.close()
    return render_template('index.html', books=books)

@app.route('/book/create', methods=('GET', 'POST'))
def create_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        isbn = request.form['isbn']
        publisher = request.form['publisher']
        total_copies = request.form['total_copies']

        conn = get_db_connection()
        conn.execute('INSERT INTO Books (title, author, genre, isbn, publisher, total_copies) VALUES (?, ?, ?, ?, ?, ?)',
                     (title, author, genre, isbn, publisher, total_copies))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('create_book.html')

@app.route('/book/<int:id>/edit', methods=('GET', 'POST'))
def edit_book(id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM Books WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        isbn = request.form['isbn']
        publisher = request.form['publisher']
        total_copies = request.form['total_copies']

        conn.execute('UPDATE Books SET title = ?, author = ?, genre = ?, isbn = ?, publisher = ?, total_copies = ? WHERE id = ?',
                     (title, author, genre, isbn, publisher, total_copies, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit_book.html', book=book)

@app.route('/book/<int:id>/delete', methods=('POST',))
def delete_book(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Books WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
