# Byreddy Uday Pujith Reddy — Personal Portfolio

A professional full-stack personal portfolio website built with **Flask** (Python) + **SQLite** backend and **HTML5 / CSS3 / Vanilla JavaScript** frontend.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3, Flask |
| Database | SQLite (structured for PostgreSQL migration) |
| Auth | Werkzeug password hashing + Flask sessions |
| CSRF | Flask-WTF CSRFProtect |

## Project Structure

```
FullStack/
├── app.py              # Application entry point
├── config.py           # Configuration classes
├── requirements.txt
├── .env.example
├── database/
│   └── schema.sql
├── models/
│   ├── db.py
│   ├── user.py
│   ├── project.py
│   └── message.py
├── routes/
│   ├── main.py
│   ├── contact.py
│   └── admin.py
├── templates/
│   ├── base.html
│   ├── index.html
│   └── admin/
└── static/
    ├── css/
    └── js/
```

## Getting Started

### 1. Clone & Navigate
```bash
cd FullStack
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
copy .env.example .env
# Edit .env with your secret key and admin credentials
```

### 5. Run the Application
```bash
python app.py
```

Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 6. Admin Dashboard
Visit: [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)

Default credentials are set via `.env` (ADMIN_USERNAME / ADMIN_PASSWORD).

## Migrating to PostgreSQL

1. Install `psycopg2`: `pip install psycopg2-binary`
2. Update `DATABASE_URL` in `.env` to your PostgreSQL connection string
3. Change SQL placeholders from `?` to `%s` in `models/db.py`
4. Run the schema against your PostgreSQL database

## Security Notes

- Never commit `.env` to version control
- Change `SECRET_KEY` and admin credentials before deploying to production
- All SQL queries use parameterized statements to prevent SQL injection
- Passwords are hashed with Werkzeug's PBKDF2/SHA-256 algorithm

## Features

- Dynamic project loading from database
- Working contact form with database storage
- Admin dashboard: add/delete/feature projects, view messages
- Responsive design (mobile, tablet, desktop)
- Dark premium theme with teal accent
- Smooth animations and micro-interactions
