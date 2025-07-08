from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, Response
from docx import Document
from flask_login import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from database import init_app, db
from models import User, MemberID, PointLog
from functools import wraps
import logging
import csv
import io
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.permanent_session_lifetime = timedelta(days=30)

load_dotenv()

# Cấu hình cơ sở dữ liệu

init_app(app)

# Tạo các bảng nếu chưa có
with app.app_context():
    db.create_all()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))

        user = User.query.get(user_id)
        if not user:
            session.clear()
            flash('Tài khoản không tồn tại hoặc đã bị xóa.', 'error')
            return redirect(url_for('login'))

        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Bạn không có quyền truy cập trang này.', 'error')
            return redirect(url_for('dashboard'))

        return f(*args, **kwargs)
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

        user = User.query.filter_by(member_id=member_id).first()

        if user and check_password_hash(user.password_hash, password):
            session.permanent = True
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['display_name'] = user.display_name
            flash(f'Chào mừng {user.display_name}!', 'success')
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

        member_id_record = MemberID.query.filter_by(member_id=member_id).first()
        if not member_id_record:
            flash('Mã thành viên không tồn tại.', 'error')
            return render_template('register.html')

        if member_id_record.is_used:
            flash('Mã thành viên đã được sử dụng.', 'error')
            return render_template('register.html')

        existing_user = User.query.filter_by(member_id=member_id).first()
        if existing_user:
            flash('Mã thành viên đã được đăng ký.', 'error')
            return render_template('register.html')

        # Tạo user mới
        password_hash = generate_password_hash(password)
        new_user = User(
            member_id=member_id,
            display_name=display_name,
            password_hash=password_hash,
            role='member',
            points=10
        )
        db.session.add(new_user)
        db.session.commit()

        # Đánh dấu mã thành viên là đã dùng
        member_id_record.is_used = True
        member_id_record.used_by = new_user.id
        db.session.commit()

        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])

    if user.role == 'admin':
        total_members = User.query.filter_by(role='member').count()
        total_points = db.session.query(db.func.sum(User.points)).filter_by(role='member').scalar() or 0
        avg_points = total_points / total_members if total_members > 0 else 0

        assigned_members = User.query.filter_by(role='member', assigned_admin_id=user.id).order_by(User.points.desc()).all()

        return render_template('admin_dashboard.html',
                               total_members=total_members,
                               total_points=total_points,
                               avg_points=round(avg_points, 1),
                               assigned_members=assigned_members)
    else:
        point_logs = db.session.query(PointLog).join(User, PointLog.admin_id == User.id) \
            .filter(PointLog.member_id == user.id) \
            .order_by(PointLog.created_at.desc()).all()

        return render_template('member_dashboard.html', user=user, point_logs=point_logs)

@app.route('/members')
@admin_required
def members():
    members = db.session.query(User).filter_by(role='member') \
        .outerjoin(User, User.id == User.assigned_admin_id) \
        .order_by(User.created_at.desc()).all()
    
    return render_template('members.html', members=members)

@app.route('/member_ids')
@admin_required
def member_ids():
    from sqlalchemy.orm import aliased
    UsedBy = aliased(User)

    member_ids = db.session.query(MemberID, UsedBy.display_name.label("used_by_name")) \
        .outerjoin(UsedBy, MemberID.used_by == UsedBy.id) \
        .order_by(MemberID.member_id).all()

    return render_template('member_ids.html', member_ids=member_ids)

@app.route('/add_member_ids', methods=['POST'])
@admin_required
def add_member_ids():
    start_num = int(request.form['start_num'])
    end_num = int(request.form['end_num'])

    for i in range(start_num, end_num + 1):
        member_id = f"MEM-{str(i).zfill(3)}"
        exists = MemberID.query.filter_by(member_id=member_id).first()
        if not exists:
            db.session.add(MemberID(member_id=member_id))

    db.session.commit()

    flash(f'Đã thêm mã thành viên từ MEM-{str(start_num).zfill(3)} đến MEM-{str(end_num).zfill(3)}', 'success')
    return redirect(url_for('member_ids'))

@app.route('/update_points/<int:member_id>', methods=['POST'])
@admin_required
def update_points(member_id):
    points_change = int(request.form['points_change'])
    reason = request.form['reason']

    user = User.query.get(member_id)
    if user:
        user.points += points_change
        log = PointLog(member_id=member_id, points_change=points_change,
                       reason=reason, admin_id=session['user_id'])
        db.session.add(log)
        db.session.commit()
        flash('Cập nhật điểm thành công!', 'success')
    else:
        flash('Không tìm thấy thành viên.', 'error')

    return redirect(url_for('members'))

@app.route('/assign_member/<int:member_id>', methods=['POST'])
@admin_required
def assign_member(member_id):
    admin_id = request.form['admin_id'] or None

    user = User.query.get(member_id)
    if user:
        user.assigned_admin_id = admin_id
        db.session.commit()
        flash('Phân công thành viên thành công!', 'success')
    else:
        flash('Không tìm thấy thành viên.', 'error')

    return redirect(url_for('members'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất thành công.', 'success')
    return redirect(url_for('login'))

@app.route('/delete_member/<int:user_id>', methods=['POST'])
@admin_required
def delete_member(user_id):
    user = User.query.get(user_id)
    if user:
        member_id_obj = MemberID.query.filter_by(member_id=user.member_id).first()
        if member_id_obj:
            member_id_obj.is_used = False
            member_id_obj.used_by = None

        db.session.delete(user)
        db.session.commit()

        flash('Đã xóa thành viên và giải phóng mã thành viên.', 'success')
    else:
        flash('Không tìm thấy người dùng.', 'error')

    return redirect(url_for('members'))

@app.route('/register_admin', methods=['GET', 'POST'])
@admin_required
def register_admin():
    if request.method == 'POST':
        member_id = request.form['member_id']
        display_name = request.form['display_name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp.', 'error')
            return render_template('register_admin.html')

        existing_user = User.query.filter_by(member_id=member_id).first()
        if existing_user:
            flash('Mã admin đã tồn tại.', 'error')
            return render_template('register_admin.html')

        password_hash = generate_password_hash(password)
        new_admin = User(member_id=member_id, display_name=display_name,
                         password_hash=password_hash, role='admin', points=10)
        db.session.add(new_admin)
        db.session.commit()

        flash('Tạo tài khoản admin thành công!', 'success')
        return redirect(url_for('login'))

    return render_template('register_admin.html')

@app.route('/delete_member_ids', methods=['POST'])
@admin_required
def delete_member_ids():
    start_id = request.form['start_id'].strip()
    end_id = request.form['end_id'].strip()

    try:
        start_num = int(start_id.split('-')[1])
        end_num = int(end_id.split('-')[1])
    except (IndexError, ValueError):
        flash('Định dạng mã không hợp lệ!', 'danger')
        return redirect(url_for('member_ids'))

    if start_num > end_num:
        flash('Mã bắt đầu phải nhỏ hơn hoặc bằng mã kết thúc!', 'danger')
        return redirect(url_for('member_ids'))

    deleted = 0
    for i in range(start_num, end_num + 1):
        mid = f"MEM-{str(i).zfill(3)}"
        member_id = MemberID.query.filter_by(member_id=mid, is_used=False).first()
        if member_id:
            db.session.delete(member_id)
            deleted += 1

    db.session.commit()
    flash(f'Đã xóa {deleted} mã thành viên chưa sử dụng.', 'success')
    return redirect(url_for('member_ids'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        display_name = request.form['display_name']
        password_current = request.form.get('password_current')
        password_new = request.form.get('password_new')
        password_confirm = request.form.get('password_confirm')

        user.display_name = display_name

        if password_current and password_new and password_confirm:
            if not check_password_hash(user.password_hash, password_current):
                flash('Mật khẩu hiện tại không đúng.', 'error')
            elif password_new != password_confirm:
                flash('Mật khẩu mới và xác nhận không khớp.', 'error')
            else:
                user.password_hash = generate_password_hash(password_new)
                flash('Đổi mật khẩu thành công.', 'success')
        else:
            flash('Cập nhật thông tin thành công.', 'success')

        db.session.commit()
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

@app.route('/admins')
@admin_required
def admins():
    current_user = User.query.get(session['user_id'])
    admins = User.query.filter_by(role='admin').order_by(User.created_at.desc()).all()
    members = User.query.filter_by(role='member').all()

    can_create = current_user.role == 'admin'
    can_edit = current_user.member_id == 'ADMIN-001'

    return render_template('admins.html', admins=admins, members=members,
                           can_create=can_create, can_edit=can_edit)

@app.route('/delete_admin/<int:user_id>', methods=['POST'])
@admin_required
def delete_admin(user_id):
    current_user = User.query.get(session['user_id'])

    if not current_user or current_user.member_id != 'ADMIN-001':
        flash('Bạn không có quyền xóa admin.', 'danger')
        return redirect(url_for('admins'))

    if user_id == current_user.id:
        flash('Không thể tự xóa chính mình.', 'danger')
        return redirect(url_for('admins'))

    admin = User.query.get(user_id)
    if admin and admin.role == 'admin':
        db.session.delete(admin)
        db.session.commit()
        flash('Đã xóa admin thành công.', 'success')
    else:
        flash('Không tìm thấy admin.', 'error')

    return redirect(url_for('admins'))

@app.route('/download_db')
@admin_required
def download_db():
    user = User.query.get(session['user_id'])
    if not user or user.member_id != 'ADMIN-001':
        flash('Bạn không có quyền tải xuống cơ sở dữ liệu.', 'error')
        return redirect(url_for('dashboard'))

    users = User.query.all()

    # Tạo file CSV trên bộ nhớ
    si = io.StringIO()
    writer = csv.writer(si)
    # Header
    writer.writerow(['ID', 'Member ID', 'Display Name', 'Role', 'Points', 'Assigned Admin ID', 'Created At'])
    # Data
    for u in users:
        writer.writerow([
            u.id, u.member_id, u.display_name, u.role, u.points,
            u.assigned_admin_id, u.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    output = si.getvalue()
    si.close()

    # Trả file về dạng response CSV
    return Response(
        output,
        mimetype='text/csv',
        headers={
            "Content-Disposition": "attachment;filename=users_export.csv"
        }
    )

# Luật sử dụng
@app.route('/rules', methods=['GET', 'POST'])
@admin_required
def rules():
    rule = Rule.query.first()
    if request.method == 'POST':
        content = request.form['content']
        if rule:
            rule.content = content
        else:
            rule = Rule(content=content)
            db.session.add(rule)
        db.session.commit()
        flash('Cập nhật nội dung luật thành công.', 'success')
        return redirect(url_for('rules'))
    return render_template('rules.html', rule=rule)

# Public view trên trang login
@app.route('/public_rules')
def public_rules():
    rule = Rule.query.first()
    return render_template('public_rules.html', rule=rule)

@app.route('/export_rules')
@admin_required
def export_rules():
    rule = Rule.query.first()
    if not rule:
        flash("Chưa có nội dung luật để xuất.", "warning")
        return redirect(url_for('rules'))

    doc = Document()
    doc.add_heading('Nội dung Luật', level=1)
    doc.add_paragraph(rule.content)

    output = io.BytesIO()
    doc.save(output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="luat.docx")

# Character abilities
@app.route('/abilities')
@login_required
def abilities():
    # Lọc
    search_faction = request.args.get('faction', '').strip()
    search_name = request.args.get('name', '').strip()
    search_desc = request.args.get('desc', '').strip()

    query = CharacterAbility.query
    if search_faction:
        query = query.filter(CharacterAbility.faction.ilike(f"%{search_faction}%"))
    if search_name:
        query = query.filter(CharacterAbility.name.ilike(f"%{search_name}%"))
    if search_desc:
        query = query.filter(CharacterAbility.description.ilike(f"%{search_desc}%"))

    abilities = query.order_by(CharacterAbility.faction, CharacterAbility.order_in_faction).all()
    is_admin = session.get('user_role') == 'admin'

    return render_template('abilities.html', abilities=abilities, is_admin=is_admin)

@app.route('/abilities/add', methods=['POST'])
@admin_required
def add_ability():
    faction = request.form['faction']
    order_in_faction = int(request.form['order'])
    name = request.form['name']
    description = request.form['description']

    new_ability = CharacterAbility(
        faction=faction,
        order_in_faction=order_in_faction,
        name=name,
        description=description
    )
    db.session.add(new_ability)
    db.session.commit()
    flash('Đã thêm chức năng.', 'success')
    return redirect(url_for('abilities'))

@app.route('/abilities/edit/<int:ability_id>', methods=['POST'])
@admin_required
def edit_ability(ability_id):
    ability = CharacterAbility.query.get(ability_id)
    if ability:
        ability.faction = request.form['faction']
        ability.order_in_faction = int(request.form['order'])
        ability.name = request.form['name']
        ability.description = request.form['description']
        db.session.commit()
        flash('Đã cập nhật.', 'success')
    return redirect(url_for('abilities'))

@app.route('/abilities/delete/<int:ability_id>', methods=['POST'])
@admin_required
def delete_ability(ability_id):
    ability = CharacterAbility.query.get(ability_id)
    if ability:
        db.session.delete(ability)
        db.session.commit()
        flash('Đã xóa chức năng.', 'success')
    return redirect(url_for('abilities'))

# Kim Bài Miễn Tử
@app.route('/kim_bai', methods=['GET', 'POST'])
@admin_required
def kim_bai():
    members = User.query.filter_by(role='member').order_by(User.display_name).all()
    return render_template('kim_bai.html', members=members)

@app.route('/update_kim_bai/<int:user_id>', methods=['POST'])
@admin_required
def update_kim_bai(user_id):
    death_count = int(request.form['death_count'])
    has_kim_bai = request.form['has_kim_bai'] == 'true'

    user = User.query.get(user_id)
    if user:
        user.death_count = death_count
        user.has_kim_bai = has_kim_bai
        db.session.commit()
        flash('Cập nhật kim bài thành công!', 'success')
    else:
        flash('Không tìm thấy người dùng.', 'error')
    return redirect(url_for('kim_bai'))

# Blacklist management
@app.route('/blacklist')
@login_required
def blacklist():
    user = User.query.get(session['user_id'])
    role_filter = request.args.get('role')

    if user.role == 'admin':
        if role_filter == 'member':
            entries = BlacklistEntry.query.join(User).filter(User.role == 'member').order_by(BlacklistEntry.created_at.desc()).all()
        elif role_filter == 'admin':
            entries = BlacklistEntry.query.join(User).filter(User.role == 'admin').order_by(BlacklistEntry.created_at.desc()).all()
        else:
            entries = BlacklistEntry.query.order_by(BlacklistEntry.created_at.desc()).all()
    else:
        entries = BlacklistEntry.query.filter_by(created_by_id=user.id).order_by(BlacklistEntry.created_at.desc()).all()

    return render_template('blacklist.html', entries=entries, user=user, role_filter=role_filter)

@app.route('/add_blacklist', methods=['POST'])
@login_required
def add_blacklist():
    name = request.form['name']
    facebook_link = request.form.get('facebook_link')
    if not name.strip():
        flash('Tên là bắt buộc!', 'danger')
        return redirect(url_for('blacklist'))
    
    new_entry = BlacklistEntry(
        name=name.strip(),
        facebook_link=facebook_link.strip() if facebook_link else None,
        created_by_id=session['user_id']
    )
    db.session.add(new_entry)
    db.session.commit()
    flash('Đã thêm vào blacklist.', 'success')
    return redirect(url_for('blacklist'))

@app.route('/delete_blacklist/<int:entry_id>', methods=['POST'])
@login_required
def delete_blacklist(entry_id):
    entry = BlacklistEntry.query.get(entry_id)
    current_user = User.query.get(session['user_id'])

    if entry and (entry.created_by_id == current_user.id or current_user.member_id == 'ADMIN-001'):
        db.session.delete(entry)
        db.session.commit()
        flash('Đã xoá mục khỏi blacklist.', 'success')
    else:
        flash('Bạn không có quyền xoá mục này.', 'danger')

    return redirect(url_for('blacklist'))

@app.route('/edit_blacklist_author/<int:entry_id>', methods=['POST'])
@admin_required
def edit_blacklist_author(entry_id):
    current_user = User.query.get(session['user_id'])
    if current_user.member_id != 'ADMIN-001':
        flash('Bạn không có quyền sửa người nhập!', 'danger')
        return redirect(url_for('blacklist'))

    new_user_id = request.form.get('new_user_id')
    entry = BlacklistEntry.query.get(entry_id)
    user_target = User.query.get(new_user_id)

    if entry and user_target:
        entry.created_by_id = user_target.id
        db.session.commit()
        flash('Đã cập nhật người nhập.', 'success')
    else:
        flash('Không tìm thấy người dùng hoặc mục!', 'danger')

    return redirect(url_for('blacklist'))



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)





