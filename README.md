# Shelfwise — Library Management System

A responsive Django application for managing a library's book collection, members, issue/return activity, and overdue fines.

## Features

- Dashboard with live counts for books, copies, active members, loans, overdue records, and calculated fines
- Book catalogue with search, add, edit, delete, and availability tracking
- Member directory with search and member status
- Book issue and return workflow with stock adjustment
- Automatic overdue fine calculation at **₹5 per overdue day**
- Responsive layout for desktop, tablet, and mobile screens
- Search filters and pagination on catalogue, member, and loan pages
- Login-protected library workspace

## Requirements

- Python 3.10 or newer
- Django 5.2 (`requirements.txt`)

## Run on Windows (VS Code / Command Prompt)

1. Extract the project ZIP.
2. Open the extracted `library_management_system` folder in VS Code.
3. Create and activate a virtual environment:

   ```bat
   python -m venv env
   env\Scripts\activate
   ```

4. Install dependencies:

   ```bat
   python -m pip install -r requirements.txt
   ```

5. Create database tables:

   ```bat
   python manage.py makemigrations library
   python manage.py migrate
   ```

6. Create an administrator account (if you do not already have one):

   ```bat
   python manage.py createsuperuser
   ```

7. Start the application:

   ```bat
   python manage.py runserver
   ```

8. Open `http://127.0.0.1:8000/` and sign in with your administrator account.

## Fine policy

A fine is calculated as ₹5 for each calendar day after a loan's due date. For an active loan, the calculation runs through today's date. For a returned loan, it stops at the recorded return date. The fine is computed from existing loan dates in Python; this enhancement does not add database fields or require a new migration.

## Updating an existing installation

If you are replacing an older version, keep a backup of your current `db.sqlite3` before copying the updated project files. The ZIP intentionally does not include a database file. Do not overwrite your existing database if you want to retain your books, members, loans, and login account.

The new interface and pagination do not require schema changes. If your project already has the Book, Member, and Loan tables, no migration is required for the UI update or fine calculation.

## Notes

- The project uses SQLite for local development.
- Bootstrap and Google Fonts are loaded from their public CDNs, so those visual assets need an internet connection in the browser.
- Before deploying publicly, set a private `SECRET_KEY`, turn `DEBUG` off, and configure `ALLOWED_HOSTS` for your domain.
