import os
import datetime
import subprocess

# Cấu hình thông tin kết nối DB từ biến môi trường
PG_HOST = os.environ.get("PGHOST")
PG_PORT = os.environ.get("PGPORT", "5432")
PG_USER = os.environ.get("PGUSER")
PG_PASSWORD = os.environ.get("PGPASSWORD")
PG_DB = os.environ.get("PGDATABASE")

# Tạo tên file theo ngày
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
filename = f"backup_{PG_DB}_{timestamp}.sql"

# Tạo lệnh backup
command = [
    "pg_dump",
    "-h", PG_HOST,
    "-p", PG_PORT,
    "-U", PG_USER,
    "-d", PG_DB,
    "-F", "c",  # Định dạng nén (custom)
    "-f", filename
]

# Đặt biến môi trường cho mật khẩu
os.environ["PGPASSWORD"] = PG_PASSWORD

# Chạy lệnh
print(f"🔄 Đang backup database: {PG_DB} -> {filename}")
subprocess.run(command, check=True)
print(f"✅ Backup hoàn tất: {filename}")
