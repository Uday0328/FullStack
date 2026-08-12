"""One-time script to reset the admin password."""
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash

db_path = os.path.join("database", "portfolio.db")
conn = sqlite3.connect(db_path)

new_password = "Admin@2026"
new_hash = generate_password_hash(new_password)

conn.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, "admin"))
conn.commit()

# Verify it works
cursor = conn.execute("SELECT password_hash FROM users WHERE username = ?", ("admin",))
row = cursor.fetchone()
verified = check_password_hash(row[0], new_password)
print(f"Password reset. Verify: {verified}")

conn.close()
