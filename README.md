# Hệ thống quản lý thành viên

Một web application đơn giản để quản lý thành viên với Flask, Bootstrap và SQLite.

## ✨ Tính năng

### 🧑‍💼 Admin
- Dashboard với thống kê tổng quan
- Quản lý danh sách thành viên
- Cộng/trừ điểm cho thành viên với lý do
- Phân công thành viên cho admin
- Quản lý mã thành viên (tạo, theo dõi sử dụng)

### 🧑‍🎓 Thành viên
- Đăng ký bằng mã ID được cấp
- Xem điểm số hiện tại
- Xem lịch sử thay đổi điểm

## 🚀 Cách chạy

### Sử dụng Docker (Khuyến nghị)

```bash
# Clone repository
git clone <your-repo-url>
cd member-management

# Chạy với Docker Compose
docker-compose up --build
```

Truy cập: http://localhost:5000

### Chạy trực tiếp với Python

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy ứng dụng
python app.py
```

## 🔐 Tài khoản mẫu

### Admin
- **Mã:** ADMIN-001
- **Mật khẩu:** admin123

### Thành viên
- **Mã:** MEM-001 đến MEM-005
- **Mật khẩu:** member123

## 📁 Cấu trúc project

```
├── app.py                 # Ứng dụng Flask chính
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── database.db          # SQLite database (tự động tạo)
├── templates/           # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── admin_dashboard.html
│   ├── member_dashboard.html
│   ├── members.html
│   └── member_ids.html
└── README.md
```

## 🌐 Deploy lên Render

1. Push code lên GitHub repository
2. Tạo Web Service mới trên Render
3. Connect với GitHub repo
4. Cấu hình:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
   - **Environment Variables:**
     - `SECRET_KEY`: your-secret-key-here
     - `PORT`: 5000

## 🔧 Cấu hình

### Environment Variables
- `SECRET_KEY`: Khóa bí mật cho Flask session (bắt buộc trong production)
- `PORT`: Port để chạy ứng dụng (mặc định: 5000)

### Database
- Sử dụng SQLite file-based database
- Database tự động khởi tạo khi chạy lần đầu
- Có sẵn dữ liệu mẫu để test

## 📊 Database Schema

### users
- id, member_id, display_name, password_hash
- role (admin/member), points, assigned_admin_id
- created_at

### member_ids
- id, member_id, is_used, used_by
- created_at

### point_logs
- id, member_id, points_change, reason
- admin_id, created_at

## 🎨 Giao diện

- Responsive design với Bootstrap 5
- Modern UI với gradient và shadows
- Dark theme cho admin dashboard
- Mobile-friendly

## 🔒 Bảo mật

- Password hashing với Werkzeug
- Session-based authentication
- Role-based access control
- CSRF protection (Flask built-in)

## 📝 License

PiuPiu License - Độc quyền Piu Piu sử dụng hệ thống này.