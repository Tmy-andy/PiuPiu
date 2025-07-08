import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    db_url = os.environ.get("DATABASE_URL")
    
    if not db_url:
        raise RuntimeError("❌ DATABASE_URL không được tìm thấy trong biến môi trường.")

    # Fix cho các URL kiểu postgres:// → postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
