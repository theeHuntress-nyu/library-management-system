# library-management-system
This is a Flask-based Library Management System that uses a normalized SQLite database to manage books, members, loans, reservations, and fines. The system includes CRUD functionality, triggers, views, a simulated procedure, and an aggregation report.

db_final.py — Main Python script containing the complete Flask web application. It includes:
Database initialization with all required tables
Business logic for books, members, reservations, loans, and fines
Views and triggers for automatic inventory and fine handling
Route handling for all CRUD operations and analytics
library.db — SQLite database file automatically created on first run. It includes:
All schema definitions (Books, Members, Reservations, Loans, Fines)
Views (BookLoansReport, AvailableBooks)
Triggers for inventory updates on loan/return
Automatically generated overdue fines
templates/ — Folder containing all HTML templates for the user interface:
index.html — Displays all books with options to add, edit, or delete
create_book.html — Form to add new books
edit_book.html — Form to update book records
members.html — Lists all registered library members
create_member.html — Form to register new members
reservations.html — View for active reservations
create_reservation.html — Form to place a reservation
fines.html — Report page showing all overdue fines with payment option
Smith_LMS Project.pptx — Final presentation including:
Overview of system architecture (3-tier)
Entity-relationship model explanation
Full walkthrough of each UI page and functionality
Screenshots and speaker notes demonstrating rubric coverage (CRUD, reporting, normalization, constraints, triggers, and views)
