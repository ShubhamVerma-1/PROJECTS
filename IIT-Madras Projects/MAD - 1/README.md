# Placement Portal Application

A web application that allows an Admin (Institute), Companies, and Students to interact with a placement system based on their roles.

---

## Project Structure

```
PLACEMENT-PORTAL/
├── templates/          # Jinja2 HTML templates
├── app.py              # Flask app entry point
├── config.py           # Environment config loader
├── models.py           # SQLAlchemy DB models
├── routes.py           # All route handlers
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (create manually)
└── README.md
```

---

## Setup and Installation

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the application
```bash
flask run
```

The app will be available at: **http://127.0.0.1:5000**

---

## Default Admin Credentials

The admin account is created automatically on first run:

| Field    | Value     |
|----------|-----------|
| Email    | `admin@1` |
| Password | `admin`   |

---

## Roles and Features

### Admin
- View dashboard with total stats (students, companies, drives, applications)
- Approve or reject company registrations
- Approve or reject placement drives
- View, search, blacklist, and reactivate student accounts
- View all applications

### Company
- Register and await admin approval
- Create, edit, close, and delete placement drives
- View applicants per drive
- Update application status (Shortlist / Select / Reject)

### Student
- Register and log in immediately
- Browse approved, active placement drives
- View full drive details (description, salary, eligibility)
- Apply to drives (deadline enforced)
- Track application statuses

---

## Notes
- The SQLite database (`instance/db.sqlite3`) is created automatically on first run.
- Passwords are securely hashed using Werkzeug.
- Sessions are managed via Flask's built-in session handling.
