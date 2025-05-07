from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='templates')
DB_NAME = 'library.db'

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

        CREATE TRIGGER IF NOT EXISTS loan_book_trigger
        AFTER INSERT ON Loans
        BEGIN
            UPDATE Books SET total_copies = total_copies - 1 WHERE id = NEW.book_id;
        END;

        CREATE TRIGGER IF NOT EXISTS return_book_trigger
        AFTER DELETE ON Loans
        BEGIN
            UPDATE Books SET total_copies = total_copies + 1 WHERE id = OLD.book_id;
        END;
        ''')
        conn.commit()
        conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_fine(loan_date_str):
    loan_date = datetime.strptime(loan_date_str, "%Y-%m-%d")
    due_date = loan_date + timedelta(days=14)
    today = datetime.now()
    if today > due_date:
        overdue_days = (today - due_date).days
        return round(overdue_days * 0.50, 2)
    return 0.00

@app.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM Books').fetchall()
    conn.close()
    return render_template('index.html', books=books)

@app.route('/book/create', methods=['GET', 'POST'])
def create_book():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('INSERT INTO Books (title, author, genre, isbn, publisher, total_copies) VALUES (?, ?, ?, ?, ?, ?)',
                     (request.form['title'], request.form['author'], request.form['genre'],
                      request.form['isbn'], request.form['publisher'], request.form['total_copies']))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('create_book.html')

@app.route('/book/<int:id>/edit', methods=['GET', 'POST'])
def edit_book(id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM Books WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        conn.execute('UPDATE Books SET title = ?, author = ?, genre = ?, isbn = ?, publisher = ?, total_copies = ? WHERE id = ?',
                     (request.form['title'], request.form['author'], request.form['genre'],
                      request.form['isbn'], request.form['publisher'], request.form['total_copies'], id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('edit_book.html', book=book)

@app.route('/book/<int:id>/delete', methods=['POST'])
def delete_book(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Books WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/members')
def list_members():
    conn = get_db_connection()
    members = conn.execute('SELECT * FROM Members').fetchall()
    conn.close()
    return render_template('members.html', members=members)

@app.route('/member/create', methods=['GET', 'POST'])
def create_member():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('INSERT INTO Members (name, email, membership_date) VALUES (?, ?, ?)',
                     (request.form['name'], request.form['email'], datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        conn.close()
        return redirect(url_for('list_members'))
    return render_template('create_member.html')

@app.route('/reservations')
def list_reservations():
    conn = get_db_connection()
    reservations = conn.execute('''
        SELECT r.id, m.name AS member_name, b.title AS book_title, r.reservation_date
        FROM Reservations r
        JOIN Members m ON r.member_id = m.id
        JOIN Books b ON r.book_id = b.id
    ''').fetchall()
    conn.close()
    return render_template('reservations.html', reservations=reservations)

@app.route('/reservation/create', methods=['GET', 'POST'])
def create_reservation():
    conn = get_db_connection()
    if request.method == 'POST':
        conn.execute('INSERT INTO Reservations (member_id, book_id, reservation_date) VALUES (?, ?, ?)',
                     (request.form['member_id'], request.form['book_id'], datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        conn.close()
        return redirect(url_for('list_reservations'))
    members = conn.execute('SELECT * FROM Members').fetchall()
    books = conn.execute('SELECT * FROM Books').fetchall()
    conn.close()
    return render_template('create_reservation.html', members=members, books=books)

@app.route('/loan/create', methods=['GET', 'POST'])
def create_loan():
    conn = get_db_connection()
    if request.method == 'POST':
        member_id = request.form['member_id']
        book_id = request.form['book_id']
        loan_date = request.form['loan_date']
        conn.execute('INSERT INTO Loans (member_id, book_id, loan_date) VALUES (?, ?, ?)',
                     (member_id, book_id, loan_date))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    members = conn.execute('SELECT * FROM Members').fetchall()
    books = conn.execute('SELECT * FROM Books WHERE total_copies > 0').fetchall()
    conn.close()
    return render_template('create_loan.html', members=members, books=books)

@app.route('/fines')
def list_fines():
    conn = get_db_connection()
    loans = conn.execute('SELECT * FROM Loans').fetchall()
    for loan in loans:
        fine_amount = calculate_fine(loan['loan_date'])
        existing = conn.execute('SELECT * FROM Fines WHERE loan_id = ?', (loan['id'],)).fetchone()
        if fine_amount > 0 and not existing:
            conn.execute('INSERT INTO Fines (loan_id, amount) VALUES (?, ?)', (loan['id'], fine_amount))
    conn.commit()
    fines = conn.execute('''
        SELECT f.id, f.amount, f.paid, l.loan_date, m.name AS member_name, b.title AS book_title
        FROM Fines f
        JOIN Loans l ON f.loan_id = l.id
        JOIN Members m ON l.member_id = m.id
        JOIN Books b ON l.book_id = b.id
    ''').fetchall()
    conn.close()
    return render_template('fines.html', fines=fines)

@app.route('/fine/<int:id>/pay', methods=['POST'])
def pay_fine(id):
    conn = get_db_connection()
    conn.execute('UPDATE Fines SET paid = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('list_fines'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
