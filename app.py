from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'member',
            points INTEGER DEFAULT 0,
            assigned_admin_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assigned_admin_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS member_ids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id TEXT UNIQUE NOT NULL,
            is_used BOOLEAN DEFAULT FALSE,
            used_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (used_by) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS point_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            points_change INTEGER NOT NULL,
            reason TEXT NOT NULL,
            admin_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES users (id),
            FOREIGN KEY (admin_id) REFERENCES users (id)
        )
    ''')

# Helper functions
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        
        if not user:
            session.clear()
            flash('Tài khoản không tồn tại hoặc đã bị xóa.', 'error')
            return redirect(url_for('login'))

        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        user = conn.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        
        if not user or user['role'] != 'admin':
            flash('Bạn không có quyền truy cập trang này.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        member_id = request.form['member_id']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE member_id = ?', (member_id,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session.permanent = True  # Cho phép giữ cookie lâu hơn
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            session['display_name'] = user['display_name']
            flash(f'Chào mừng {user["display_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Mã thành viên hoặc mật khẩu không đúng.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        member_id = request.form['member_id']
        display_name = request.form['display_name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp.', 'error')
            return render_template('register.html')
        
        conn = get_db_connection()
        
        # Check if member ID exists and is available
        member_id_record = conn.execute('SELECT * FROM member_ids WHERE member_id = ?', (member_id,)).fetchone()
        if not member_id_record:
            flash('Mã thành viên không tồn tại.', 'error')
            conn.close()
            return render_template('register.html')
        
        if member_id_record['is_used']:
            flash('Mã thành viên đã được sử dụng.', 'error')
            conn.close()
            return render_template('register.html')
        
        # Check if member_id already exists in users table
        existing_user = conn.execute('SELECT * FROM users WHERE member_id = ?', (member_id,)).fetchone()
        if existing_user:
            flash('Mã thành viên đã được đăng ký.', 'error')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (member_id, display_name, password_hash, role, points)
            VALUES (?, ?, ?, ?, ?)
        ''', (member_id, display_name, password_hash, 'member', 10))
        
        user_id = cursor.lastrowid
        
        # Mark member ID as used
        cursor.execute('UPDATE member_ids SET is_used = TRUE, used_by = ? WHERE member_id = ?', 
                      (user_id, member_id))
        
        conn.commit()
        conn.close()
        
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if user['role'] == 'admin':
        # Admin dashboard
        total_members = conn.execute('SELECT COUNT(*) as count FROM users WHERE role = "member"').fetchone()['count']
        total_points = conn.execute('SELECT SUM(points) as total FROM users WHERE role = "member"').fetchone()['total'] or 0
        avg_points = total_points / total_members if total_members > 0 else 0
        
        # Get members assigned to this admin
        assigned_members = conn.execute('''
            SELECT * FROM users 
            WHERE role = "member" AND assigned_admin_id = ?
            ORDER BY points DESC
        ''', (session['user_id'],)).fetchall()
        
        conn.close()
        return render_template('admin_dashboard.html', 
                             total_members=total_members,
                             total_points=total_points,
                             avg_points=round(avg_points, 1),
                             assigned_members=assigned_members)
    else:
        # Member dashboard
        point_logs = conn.execute('''
            SELECT pl.*, u.display_name as admin_name
            FROM point_logs pl
            JOIN users u ON pl.admin_id = u.id
            WHERE pl.member_id = ?
            ORDER BY pl.created_at DESC
        ''', (session['user_id'],)).fetchall()
        
        conn.close()
        return render_template('member_dashboard.html', user=user, point_logs=point_logs)

@app.route('/members')
@admin_required
def members():
    conn = get_db_connection()
    members = conn.execute('''
        SELECT u.*, a.display_name as admin_name
        FROM users u
        LEFT JOIN users a ON u.assigned_admin_id = a.id
        WHERE u.role = "member"
        ORDER BY u.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('members.html', members=members)

@app.route('/member_ids')
@admin_required
def member_ids():
    conn = get_db_connection()
    member_ids = conn.execute('''
        SELECT mi.*, u.display_name as used_by_name
        FROM member_ids mi
        LEFT JOIN users u ON mi.used_by = u.id
        ORDER BY mi.member_id
    ''').fetchall()
    conn.close()
    return render_template('member_ids.html', member_ids=member_ids)

@app.route('/add_member_ids', methods=['POST'])
@admin_required
def add_member_ids():
    start_num = int(request.form['start_num'])
    end_num = int(request.form['end_num'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for i in range(start_num, end_num + 1):
        member_id = f'MEM-{str(i).zfill(3)}'
        cursor.execute('INSERT OR IGNORE INTO member_ids (member_id) VALUES (?)', (member_id,))
    
    conn.commit()
    conn.close()
    
    flash(f'Đã thêm mã thành viên từ MEM-{str(start_num).zfill(3)} đến MEM-{str(end_num).zfill(3)}', 'success')
    return redirect(url_for('member_ids'))

@app.route('/update_points/<int:member_id>', methods=['POST'])
@admin_required
def update_points(member_id):
    points_change = int(request.form['points_change'])
    reason = request.form['reason']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update member points
    cursor.execute('UPDATE users SET points = points + ? WHERE id = ?', (points_change, member_id))
    
    # Add to point log
    cursor.execute('''
        INSERT INTO point_logs (member_id, points_change, reason, admin_id)
        VALUES (?, ?, ?, ?)
    ''', (member_id, points_change, reason, session['user_id']))
    
    conn.commit()
    conn.close()
    
    flash('Cập nhật điểm thành công!', 'success')
    return redirect(url_for('members'))

@app.route('/assign_member/<int:member_id>', methods=['POST'])
@admin_required
def assign_member(member_id):
    admin_id = request.form['admin_id'] if request.form['admin_id'] else None
    
    conn = get_db_connection()
    conn.execute('UPDATE users SET assigned_admin_id = ? WHERE id = ?', (admin_id, member_id))
    conn.commit()
    conn.close()
    
    flash('Phân công thành viên thành công!', 'success')
    return redirect(url_for('members'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất thành công.', 'success')
    return redirect(url_for('login'))

@app.route('/delete_member/<int:user_id>', methods=['POST'])
def delete_member(user_id):
    conn = get_db_connection()

    # Lấy member_id của user bị xóa (nếu cần dùng)
    user = conn.execute('SELECT member_id FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        member_id = user['member_id']
        
        # Cập nhật lại member_ids để đánh dấu là chưa dùng
        conn.execute('''
            UPDATE member_ids
            SET is_used = FALSE, used_by = NULL
            WHERE member_id = ?
        ''', (member_id,))

        # Xóa user
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        flash('Đã xóa thành viên và giải phóng mã thành viên.', 'success')
    else:
        flash('Không tìm thấy người dùng.', 'error')

    conn.close()
    return redirect(url_for('members'))


@app.route('/register_admin', methods=['GET', 'POST'])
@admin_required  # Chỉ admin mới được tạo admin mới, hoặc bạn có thể bỏ nếu muốn ai cũng đăng ký admin
def register_admin():
    if request.method == 'POST':
        member_id = request.form['member_id']
        display_name = request.form['display_name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp.', 'error')
            return render_template('register_admin.html')
        conn = get_db_connection()
        # Kiểm tra member_id đã tồn tại chưa
        existing_user = conn.execute('SELECT * FROM users WHERE member_id = ?', (member_id,)).fetchone()
        if existing_user:
            flash('Mã thành viên đã tồn tại.', 'error')
            conn.close()
            return render_template('register_admin.html')
        password_hash = generate_password_hash(password)
        conn.execute('''
            INSERT INTO users (member_id, display_name, password_hash, role, points)
            VALUES (?, ?, ?, ?, ?)
        ''', (member_id, display_name, password_hash, 'admin', 0))
        conn.commit()
        conn.close()
        flash('Tạo tài khoản admin thành công!', 'success')
        return redirect(url_for('login'))
    return render_template('register_admin.html')

@app.route('/delete_member_ids', methods=['POST'])
@admin_required
def delete_member_ids():
    start_id = request.form['start_id'].strip()
    end_id = request.form['end_id'].strip()
    # Lấy số thứ tự từ mã (giả sử mã dạng MEM-001)
    try:
        start_num = int(start_id.split('-')[1])
        end_num = int(end_id.split('-')[1])
    except (IndexError, ValueError):
        flash('Định dạng mã không hợp lệ!', 'danger')
        return redirect(url_for('member_ids'))
    if start_num > end_num:
        flash('Mã bắt đầu phải nhỏ hơn hoặc bằng mã kết thúc!', 'danger')
        return redirect(url_for('member_ids'))
    conn = get_db_connection()
    deleted = 0
    for i in range(start_num, end_num + 1):
        mid = f"MEM-{str(i).zfill(3)}"
        # Chỉ xóa nếu mã chưa được dùng
        result = conn.execute('DELETE FROM member_ids WHERE member_id = ? AND is_used = 0', (mid,))
        deleted += result.rowcount
    conn.commit()
    conn.close()
    flash(f'Đã xóa {deleted} mã thành viên chưa sử dụng.', 'success')
    return redirect(url_for('member_ids'))

from werkzeug.security import check_password_hash, generate_password_hash

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if request.method == 'POST':
        display_name = request.form['display_name']
        password_current = request.form.get('password_current')
        password_new = request.form.get('password_new')
        password_confirm = request.form.get('password_confirm')
        # Cập nhật tên
        conn.execute('UPDATE users SET display_name = ? WHERE id = ?', (display_name, session['user_id']))
        # Nếu có nhập mật khẩu mới thì xử lý đổi mật khẩu
        if password_current and password_new and password_confirm:
            if not check_password_hash(user['password_hash'], password_current):
                flash('Mật khẩu hiện tại không đúng.', 'error')
            elif password_new != password_confirm:
                flash('Mật khẩu mới và xác nhận không khớp.', 'error')
            else:
                new_hash = generate_password_hash(password_new)
                conn.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, session['user_id']))
                flash('Đổi mật khẩu thành công.', 'success')
        else:
            flash('Cập nhật thông tin thành công.', 'success')
        conn.commit()
        conn.close()
        return redirect(url_for('profile'))
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/admins')
def admins():
    conn = get_db_connection()
    admins = conn.execute('SELECT * FROM users WHERE role = "admin"').fetchall()
    conn.close()
    
    # Kiểm tra quyền sửa: chỉ ADMIN-030 mới có thể chỉnh sửa
    current_user_id = session.get('user_id')
    can_edit = False
    if current_user_id:
        conn = get_db_connection()
        user = conn.execute('SELECT member_id FROM users WHERE id = ?', (current_user_id,)).fetchone()
        conn.close()
        if user and user['member_id'] == 'ADMIN-001':
            can_edit = True

    return render_template('admins.html', admins=admins, can_edit=can_edit)

@app.route('/delete_admin/<int:user_id>', methods=['POST'])
def delete_admin(user_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        flash('Bạn cần đăng nhập.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    current_user = conn.execute('SELECT member_id FROM users WHERE id = ?', (current_user_id,)).fetchone()
    
    if not current_user or current_user['member_id'] != 'ADMIN-001':
        flash('Bạn không có quyền xóa admin.', 'danger')
        conn.close()
        return redirect(url_for('admins'))

    # Không cho tự xóa chính mình
    if user_id == current_user_id:
        flash('Không thể tự xóa chính mình.', 'danger')
        conn.close()
        return redirect(url_for('admins'))

    # Xóa admin
    conn.execute('DELETE FROM users WHERE id = ? AND role = "admin"', (user_id,))
    conn.commit()
    conn.close()
    flash('Đã xóa admin thành công.', 'success')
    return redirect(url_for('admins'))


if __name__ == '__main__':
    if not os.path.exists('database.db'):
        init_db()
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))




