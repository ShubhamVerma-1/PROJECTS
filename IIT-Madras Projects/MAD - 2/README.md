# Placement Portal Application

A campus recruitment management system that lets an **Admin (Institute)**, **Companies**, and **Students** interact with the placement process based on their role — replacing spreadsheet/email-based coordination with a single web application.

---

## Tech Stack

| Layer          | Technology                                    |
|----------------|------------------------------------------------|
| Backend API    | Flask, Flask-SQLAlchemy, Flask-JWT-Extended     |
| Database       | SQLite                                          |
| Frontend       | Vue 3 (Composition API), Bootstrap 5, Axios     |
| Caching        | Redis (via Flask-Caching)                       |
| Async Jobs     | Celery + Celery Beat (Redis as broker/backend)  |
| Email          | Flask-Mail + MailHog (local SMTP testing)       |
| Auth           | JWT (role embedded in token claims)             |

---

## Project Structure

```
placement-portal/
├── backend/
│   ├── app.py                  # App factory, Celery config, admin auto-seed
│   ├── config.py                # Env-driven config (DB, Redis, JWT, Mail)
│   ├── extensions.py            # Shared db / jwt / cache / mail / celery instances
│   ├── models.py                 # User, CompanyProfile, StudentProfile, Drive, Application
│   ├── utils.py                  # role_required decorator, send_email helper
│   ├── routes/
│   │   ├── auth.py               # Register, login, /me
│   │   ├── admin.py              # Dashboard, approvals, blacklist, search
│   │   ├── company.py            # Drives, applications, interviews, resume access
│   │   └── student.py            # Profile, resume upload, drive browsing, applications
│   ├── tasks/
│   │   ├── reminders.py          # Daily deadline reminder emails (Celery Beat)
│   │   ├── reports.py            # Monthly HTML placement report (Celery Beat)
│   │   ├── exports.py            # Student-triggered async CSV export
│   │   └── maintenance.py        # Auto-close drives past their deadline
│   ├── uploads/resumes/          # Uploaded student resumes (PDF)
│   └── instance/app.db           # SQLite database (auto-created)
│
└── frontend/
    └── src/
        ├── views/                 # LoginView, RegisterView, AdminDashboard,
        │                          # CompanyDashboard, StudentDashboard
        ├── store/auth.js          # Reactive auth state + isLoggedIn/hasRole helpers
        ├── services/api.js        # Axios instance, JWT interceptor, 401/403 handling
        ├── router/index.js        # Route guards (auth + role-based)
        ├── App.vue
        └── main.js
```

---

## Setup and Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Redis server
- [MailHog](https://github.com/mailhog/MailHog) (for local email testing)

### 1. Backend (run in WSL)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# create a .env file if you want to override config.py defaults
# (SECRET_KEY, JWT_SECRET_KEY, DATABASE_URL, REDIS_URL, ADMIN_EMAIL, etc.)

flask run
```
The API will be available at **http://127.0.0.1:5000**. On first run, the database tables are created and a single Admin account is seeded automatically (admin registration is intentionally not allowed).

### 2. Redis

```bash
redis-server
```

### 3. Celery worker + Celery Beat (separate terminals, in WSL)

```bash
celery -A app.celery worker --loglevel=info
celery -A app.celery beat --loglevel=info
```

### 4. MailHog (in WSL)

```bash
mailhog
```
Sent emails (reminders, reports) can be viewed at **http://localhost:8025**.

### 5. Frontend (run in Git Bash / PowerShell)

```bash
cd frontend
npm install
npm run dev
```
The app will be available at **http://localhost:5173**.

---

## Default Admin Credentials

The Admin is the only pre-seeded user; there is no admin self-registration.

| Field    | Value                            |
|----------|-----------------------------------|
| Email    | `admin@placementportal.com`       |
| Password | `shubham`                         |

Both can be overridden via the `ADMIN_EMAIL` and `ADMIN_DEFAULT_PASSWORD` environment variables.

---

## Roles and Features

### Admin
- Dashboard showing total students, total companies, and total drives (cached in Redis for 60 seconds)
- Approve or reject company registrations
- Approve or reject placement drives
- View all companies, students, drives, and applications
- Search students and companies by name/email
- Blacklist or reactivate any student or company (blacklisting a company auto-closes its open drives)

### Company
- Self-register a company profile (locked out of creating drives until admin-approved)
- Dashboard with company details, created drives, and applicant count per drive
- Create placement drives (eligibility criteria: branch, minimum CGPA, graduation year)
- Close a drive early
- View applications received per drive, and each applicant's resume
- Move applications through the stages `applied → shortlisted → selected/rejected`
- Schedule interviews (date + details) for shortlisted students

### Student
- Self-register and log in
- Edit profile (branch, CGPA, graduation year) and upload a resume (PDF only)
- Browse admin-approved drives with search and an eligibility indicator per drive
- Apply to a drive (blocked on duplicate applications, closed drives, passed deadlines, or ineligibility)
- Track application status and interview details
- View full application/placement history
- Export application history as a CSV (async job, see below)

---

## Background Jobs (Celery)

| Job                        | Trigger                                  | Description |
|----------------------------|-------------------------------------------|-------------|
| **Deadline reminders**     | Celery Beat — daily                       | Emails students about drives with an approaching application deadline |
| **Monthly activity report**| Celery Beat — 1st of every month          | Builds an HTML report (drives run, students applied, students selected) and emails it to the Admin |
| **CSV export**             | Student-triggered from the dashboard      | Generates a CSV of the student's application history (student ID, company, drive title, status, dates); the frontend polls the task ID and shows an alert once it's ready |
| **Auto-close expired drives** | Celery Beat — daily                    | Closes any approved drive whose application deadline has passed |

---

## Caching

Two deliberately different caching approaches are used, to demonstrate both styles:

- **Decorator-based**: `@cache.cached(timeout=60)` on the admin dashboard endpoint
- **Manual get/set**: plain `cache.get` / `cache.set` on the student drive listing, explicitly invalidated whenever a drive's status changes (approve/reject/close) or a company is blacklisted

---

## Notes
- Passwords are hashed with Werkzeug's `generate_password_hash`.
- Auth is stateless JWT (no server-side sessions); the token carries the user's role and name as claims so protected routes can authorize without an extra database lookup.
- The application status lifecycle is fixed to four states: `applied`, `shortlisted`, `selected`, `rejected`.
