FROM python:3.11-slim

WORKDIR /app

# Cài thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ project
COPY . .

# Khởi tạo DB nếu chưa có
# (nên tách logic tạo DB sang 1 script riêng nếu bạn không muốn tạo lại mỗi lần khởi động)

ENV PORT=5000
EXPOSE $PORT
# Biến môi trường Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Chạy ứng dụng
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]