import os
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()


# SQLite source
sqlite_url = 'sqlite:///database.db'
sqlite_engine = create_engine(sqlite_url)
sqlite_metadata = MetaData()
sqlite_metadata.reflect(bind=sqlite_engine)
SQLiteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SQLiteSession()

# PostgreSQL destination (Railway)
postgres_url = os.environ.get("DATABASE_URL")
if postgres_url.startswith("postgres://"):
    postgres_url = postgres_url.replace("postgres://", "postgresql://")

postgres_engine = create_engine(postgres_url)
postgres_metadata = MetaData()
postgres_metadata.reflect(bind=postgres_engine)
PostgresSession = sessionmaker(bind=postgres_engine)
postgres_session = PostgresSession()

# Chuyển từng bảng
for table_name in sqlite_metadata.tables:
    print(f"🛠️ Đang chuyển bảng: {table_name}")
    sqlite_table = Table(table_name, sqlite_metadata, autoload_with=sqlite_engine)
    postgres_table = Table(table_name, postgres_metadata, autoload_with=postgres_engine)

    rows = sqlite_session.execute(sqlite_table.select()).mappings().all()

    if rows:
        postgres_session.execute(postgres_table.insert(), rows)
        postgres_session.commit()

print("✅ Hoàn tất chuyển dữ liệu từ SQLite sang PostgreSQL.")
