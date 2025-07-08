import os
import sqlite3
from models import db, User, MemberID, PointLog
from flask import Flask
from database import init_app

# Setup Flask + PostgreSQL
app = Flask(__name__)
init_app(app)
app.app_context().push()

# Kết nối SQLite
sqlite_conn = sqlite3.connect("database.db")
sqlite_cursor = sqlite_conn.cursor()

# Migrate users
sqlite_cursor.execute("SELECT id, member_id, display_name, password_hash, role, points, assigned_admin_id, created_at FROM users")
for row in sqlite_cursor.fetchall():
    db.session.add(User(
        id=row[0], member_id=row[1], display_name=row[2],
        password_hash=row[3], role=row[4], points=row[5],
        assigned_admin_id=row[6], created_at=row[7]
    ))

# Migrate member_ids
sqlite_cursor.execute("SELECT id, member_id, is_used, used_by, created_at FROM member_ids")
for row in sqlite_cursor.fetchall():
    db.session.add(MemberID(
        id=row[0], member_id=row[1], is_used=bool(row[2]),
        used_by=row[3], created_at=row[4]
    ))

# Migrate point_logs
sqlite_cursor.execute("SELECT id, member_id, points_change, reason, admin_id, created_at FROM point_logs")
for row in sqlite_cursor.fetchall():
    db.session.add(PointLog(
        id=row[0], member_id=row[1], points_change=row[2],
        reason=row[3], admin_id=row[4], created_at=row[5]
    ))

db.session.commit()
print("✅ Migrate hoàn tất.")