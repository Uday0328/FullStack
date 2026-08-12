import sqlite3, os
from werkzeug.security import check_password_hash, generate_password_hash

db_path = os.path.join("database", "portfolio.db")
print("DB exists:", os.path.exists(db_path))

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT id, username, password_hash FROM users")
rows = c.fetchall()
for row in rows:
    uid = row["id"]
    uname = row["username"]
    phash = row["password_hash"]
    print(f"User #{uid}: {uname}")
    print(f"  Hash prefix: {phash[:60]}")
    result = check_password_hash(phash, "Admin@2026")
    print(f"  Verify 'Admin@2026': {result}")

if not rows:
    print("NO USERS FOUND IN DB!")

# Check projects
c.execute("SELECT id, title FROM projects")
for row in c.fetchall():
    print(f"Project #{row['id']}: {row['title']}")

# Check messages
c.execute("SELECT COUNT(*) as cnt FROM messages")
print(f"Messages: {c.fetchone()['cnt']}")

conn.close()
