# library-management-system
This is a Flask-based Library Management System that uses a normalized SQLite database to manage books, members, loans, reservations, and fines. The system includes CRUD functionality, triggers, views, a simulated procedure, and an aggregation report.

- db_final.py — Main Python script containing the Flask web app, database initialization, business logic, and trigger setup

- library.db — SQLite database file with all tables, sample data, views, and triggers

- templates/ — Folder containing the HTML templates used for the web interface:

- index.html — Displays the list of books with options to edit or delete

- create_book.html — Form for adding new books

- edit_book.html — Form for updating existing book records

- Smith_LMS Project.pptx — Final presentation with speaker notes and screenshots demonstrating CRUD, reporting, and architecture
