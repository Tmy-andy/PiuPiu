print("✅ Flask khởi động...")
import os
import traceback
print("✅ Flask đang được yêu cầu chạy ở cổng :", os.environ.get("PORT"))
print("📦 Environment:", dict(os.environ))

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, Response, abort
from docx import Document
from flask_login import login_required, LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from datetime import datetime
from database import init_app, db
from models import User, MemberID, PointLog, Rule, CharacterAbility, BlacklistEntry, KimBaiLog, PlayerOffRequest, GamePlayer, GameHistory
from functools import wraps
from sqlalchemy.orm import aliased
from flask_sqlalchemy import SQLAlchemy
import logging
from zipfile import ZipFile
import tempfile
from sqlalchemy.sql import func
import csv
import io
from flask_migrate import Migrate
from flask_login import current_user
from dotenv import load_dotenv

load_dotenv()

try:
    app = Flask(__name__)
    app.logger.setLevel(logging.DEBUG)
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.permanent_session_lifetime = timedelta(days=30)


    init_app(app)

    with app.app_context():
        db.create_all()

    print("✅ Flask khởi động...")

except Exception as e:
    print("🛑 Lỗi khi khởi tạo Flask app:")
    traceback.print_exc()

from models import db

migrate = Migrate(app, db)

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

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

    from datetime import datetime
    warning_count = 0
    now = datetime.utcnow()

    users = User.query.all()
    for u in users:
        # ❌ Nếu chưa có is_active thì bỏ dòng này
        # if not u.is_active:
        #     continue

        # Kiểm tra có đang xin nghỉ không
        on_leave = PlayerOffRequest.query.filter(
            PlayerOffRequest.user_id == u.id,
            PlayerOffRequest.start_date <= now.date(),
            PlayerOffRequest.end_date >= now.date()
        ).first()

        if on_leave:
            continue

        # Lấy lần chơi gần nhất
        last_game = (
            GamePlayer.query
            .filter_by(player_id=u.id)
            .join(GameHistory)
            .order_by(GameHistory.created_at.desc())
            .first()
        )
        last_play_time = last_game.game.created_at if last_game else None

        if not last_play_time or (now - last_play_time).days > 7:
            warning_count += 1

    return dict(user=user, warning_count=warning_count)



# Error handlers
@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("errors/500.html"), 500

# Routes
@app.route('/ping')
def ping():
    return "pong"

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

        return render_template(
            'admin_dashboard.html',
            total_members=total_members,
            total_points=total_points,
            avg_points=round(avg_points, 1),
            assigned_members=assigned_members,
            admin_points=user.points  # 👈 thêm dòng này
        )
    else:
        point_logs = db.session.query(PointLog).join(User, PointLog.admin_id == User.id) \
            .filter(PointLog.member_id == user.id) \
            .order_by(PointLog.created_at.desc()).all()

        return render_template('member_dashboard.html', user=user, point_logs=point_logs)

@app.route('/members')
@admin_required
def members():
    Admin = aliased(User)

    results = db.session.query(
        User,
        Admin.display_name.label("admin_name")
    ).outerjoin(Admin, User.assigned_admin_id == Admin.id) \
     .filter(User.role == 'member') \
     .order_by(User.created_at.desc()).all()

    members = []
    for user, admin_name in results:
        user.admin_name = admin_name
        members.append(user)

    # ✅ Lấy tất cả admin để hiện trong modal chọn
    all_admins = User.query.filter_by(role='admin').order_by(User.display_name).all()

    return render_template('members.html', members=members, all_admins=all_admins)

@app.route('/assign_member/<int:user_id>', methods=['POST'])
@admin_required
def assign_member(user_id):
    try:
        new_admin_id = request.form.get('admin_id')

        user = User.query.get(user_id)
        if not user or user.role != 'member':
            flash('Không tìm thấy thành viên hợp lệ.', 'danger')
            return redirect(url_for('members'))

        if new_admin_id:
            try:
                new_admin_id = int(new_admin_id)
                new_admin = User.query.get(new_admin_id)
            except ValueError:
                flash('ID admin không hợp lệ.', 'danger')
                return redirect(url_for('members'))

            if not new_admin or new_admin.role != 'admin':
                flash('Admin không hợp lệ.', 'danger')
                return redirect(url_for('members'))

            user.assigned_admin_id = new_admin.id
        else:
            user.assigned_admin_id = None

        db.session.commit()
        flash(f'Đã cập nhật admin phụ trách cho {user.display_name}.', 'success')
        return redirect(url_for('members'))

    except Exception as e:
        print("Lỗi ở /assign_member:", e)
        flash('Đã xảy ra lỗi nội bộ.', 'danger')
        return redirect(url_for('members'))

@app.route('/member_ids')
@admin_required
def member_ids():
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
        # Nếu không cho tự cộng điểm, bật đoạn này
        # if user.id == session['user_id']:
        #     flash('Bạn không thể tự cộng điểm cho chính mình.', 'warning')
        #     return redirect(request.referrer or url_for('dashboard'))

        user.points += points_change
        log = PointLog(member_id=member_id,
                       points_change=points_change,
                       reason=reason,
                       admin_id=session['user_id'])
        db.session.add(log)
        db.session.commit()
        flash('Cập nhật điểm thành công!', 'success')
    else:
        flash('Không tìm thấy người dùng.', 'danger')

    return redirect(request.referrer or url_for('dashboard'))

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

    admins = User.query.filter_by(role='admin').order_by(User.created_at.desc()).all()
    members = User.query.filter_by(role='member').all()

    can_create = current_user.role == 'admin'
    can_edit = current_user.member_id == 'ADMIN-001'

    return render_template('admins.html', admins=admins, members=members,
                           can_create=can_create, can_edit=can_edit)

@app.route('/delete_admin/<int:user_id>', methods=['POST'])
@admin_required
def delete_admin(user_id):


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

@app.route('/update_admin_points/<int:user_id>', methods=['POST'])
@admin_required
def update_admin_points(user_id):


    if not current_user or current_user.member_id != 'ADMIN-001':
        flash('Bạn không có quyền cập nhật điểm admin.', 'danger')
        return redirect(url_for('admins'))

    admin = User.query.get(user_id)
    if admin and admin.role == 'admin':
        try:
            points = int(request.form['points'])
            admin.points = points
            db.session.commit()
            flash('Cập nhật điểm thành công.', 'success')
        except ValueError:
            flash('Giá trị điểm không hợp lệ.', 'danger')
    else:
        flash('Không tìm thấy admin.', 'danger')

    return redirect(url_for('admins'))

@app.route('/download_db')
@admin_required
def download_db():
    user = User.query.get(session['user_id'])
    if not user or user.member_id not in ['ADMIN-001', 'ADMIN-030']:
        flash('Bạn không có quyền tải xuống cơ sở dữ liệu.', 'error')
        return redirect(url_for('dashboard'))

    temp_dir = tempfile.TemporaryDirectory()
    zip_path = os.path.join(temp_dir.name, "full_database_export.zip")

    with ZipFile(zip_path, 'w') as zipf:
        def add_csv(filename, headers, rows):
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(headers)
            writer.writerows(rows)
            zipf.writestr(filename, buffer.getvalue())
            buffer.close()

        # 1. Users
        users = User.query.all()
        add_csv("users.csv",
                ['ID', 'Member ID', 'Display Name', 'Role', 'Points', 'Assigned Admin ID', 'Death Count', 'Has Kim Bài', 'Created At'],
                [[u.id, u.member_id, u.display_name, u.role, u.points, u.assigned_admin_id, u.death_count, u.has_kim_bai, u.created_at.strftime('%Y-%m-%d %H:%M:%S')] for u in users])

        # 2. Member IDs
        members = MemberID.query.all()
        add_csv("member_ids.csv",
                ['ID', 'Member ID', 'Is Used', 'Used By', 'Created At'],
                [[m.id, m.member_id, m.is_used, m.used_by, m.created_at.strftime('%Y-%m-%d %H:%M:%S')] for m in members])

        # 3. Point Logs
        logs = PointLog.query.all()
        add_csv("point_logs.csv",
                ['ID', 'Member ID', 'Points Change', 'Reason', 'Admin ID', 'Created At'],
                [[l.id, l.member_id, l.points_change, l.reason, l.admin_id, l.created_at.strftime('%Y-%m-%d %H:%M:%S')] for l in logs])

        # 4. Blacklist
        entries = BlacklistEntry.query.all()
        add_csv("blacklist.csv",
                ['ID', 'Name', 'Facebook Link', 'Created By ID', 'Created At'],
                [[b.id, b.name, b.facebook_link, b.created_by_id, b.created_at.strftime('%Y-%m-%d %H:%M:%S')] for b in entries])

        # 5. Character Abilities
        abilities = CharacterAbility.query.all()
        add_csv("character_ability.csv",
                ['ID', 'Faction', 'Order', 'Name', 'Description', 'Created At'],
                [[a.id, a.faction, a.order_in_faction, a.name, a.description, a.created_at.strftime('%Y-%m-%d %H:%M:%S')] for a in abilities])

        # 6. Rules
        rules = Rule.query.all()
        add_csv("rules.csv",
                ['ID', 'Content', 'Updated At'],
                [[r.id, r.content, r.updated_at.strftime('%Y-%m-%d %H:%M:%S')] for r in rules])

    return send_file(zip_path, as_attachment=True, download_name="full_database_export.zip")

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
FACTIONS = ["Phe Dân", "Phe Sói", "Phe Ba", "Đổi Phe"]

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

    # Tính STT kế tiếp cho từng phe
    FACTIONS = ['Phe Dân', 'Phe Sói', 'Phe Ba', 'Đổi Phe']
    next_orders = {
        faction: (db.session.query(db.func.max(CharacterAbility.order_in_faction))
                  .filter_by(faction=faction).scalar() or 0) + 1
        for faction in FACTIONS
    }

    # Nhóm chức năng theo phe và sắp xếp theo thứ tự FACTIONS
    grouped_abilities = {f: [] for f in FACTIONS}
    for a in abilities:
        grouped_abilities.setdefault(a.faction, []).append(a)

    # Đảm bảo thứ tự phe khi truyền vào template
    grouped_abilities_ordered = {f: grouped_abilities.get(f, []) for f in FACTIONS}

    return render_template(
        'abilities.html',
        abilities=abilities,
        is_admin=is_admin,
        next_orders=next_orders,
        grouped_abilities=grouped_abilities_ordered
    )


@app.route('/abilities/add', methods=['POST'])
@admin_required
def add_ability():
    faction = request.form['faction']
    order_in_faction = request.form.get('order')
    
    if not order_in_faction or order_in_faction.strip() == '':
        max_order = db.session.query(db.func.max(CharacterAbility.order_in_faction)).filter_by(faction=faction).scalar()
        order_in_faction = (max_order or 0) + 1
    else:
        order_in_faction = int(order_in_faction)

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
    else:
        flash('Không tìm thấy chức năng.', 'danger')
    return redirect(url_for('abilities'))


@app.route('/abilities/delete/<int:ability_id>', methods=['POST'])
@admin_required
def delete_ability(ability_id):
    ability = CharacterAbility.query.get(ability_id)
    if ability:
        db.session.delete(ability)
        db.session.commit()
        flash('Đã xóa chức năng.', 'success')
    else:
        flash('Không tìm thấy chức năng.', 'danger')
    return redirect(url_for('abilities'))

# Kim Bài Miễn Tử
@app.route('/kim_bai')
@login_required
def kim_bai():
    members = User.query.filter_by(role='member').order_by(User.display_name).all()
    return render_template('kim_bai.html', members=members)

@app.route('/increase_death/<int:user_id>', methods=['POST'])
@admin_required
def increase_death(user_id):
    user = User.query.get(user_id)
    if user:
        user.death_count += 1
        # Nếu death_count chia hết cho 2 → cấp kim bài
        if user.death_count > 0 and user.death_count % 2 == 0:
            user.has_kim_bai = True
        db.session.commit()

        log = KimBaiLog(user_id=user.id, timestamp=datetime.utcnow())
        db.session.add(log)
        db.session.commit()

        flash('Đã tăng lượt chết.', 'success')
    return redirect(url_for('kim_bai'))

@app.route('/use_kim_bai/<int:user_id>', methods=['POST'])
@admin_required
def use_kim_bai(user_id):
    user = User.query.get(user_id)
    if user and user.has_kim_bai:
        user.has_kim_bai = False
        db.session.commit()
        flash('Đã sử dụng kim bài.', 'success')
    else:
        flash('Không có kim bài để dùng.', 'danger')
    return redirect(url_for('kim_bai'))

@app.route('/decrease_death/<int:user_id>', methods=['POST'])
@admin_required
def decrease_death(user_id):
    user = User.query.get(user_id)
    if user and user.death_count > 0:
        user.death_count -= 1

        # Cập nhật lại trạng thái kim bài:
        if user.death_count > 0 and user.death_count % 2 == 0:
            user.has_kim_bai = True
        else:
            user.has_kim_bai = False

        db.session.commit()
        flash('Đã giảm lượt chết.', 'success')
    else:
        flash('Không thể giảm nữa.', 'warning')
    return redirect(url_for('kim_bai'))


#Top
@app.route('/top_tier')
@login_required
def top_tier():
    # Top 3 chết nhiều nhất tháng
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year

    top_deaths = (
        db.session.query(User.display_name, func.count(KimBaiLog.id).label("death_count"))
        .join(KimBaiLog)
        .filter(func.extract('month', KimBaiLog.timestamp) == current_month)
        .filter(func.extract('year', KimBaiLog.timestamp) == current_year)
        .group_by(User.id)
        .order_by(func.count(KimBaiLog.id).desc())
        .limit(3)
        .all()
    )

    return render_template("top_tier.html", top_deaths=top_deaths, now=datetime.utcnow())


# Blacklist management
@app.route('/blacklist', methods=['GET', 'POST'])
@login_required
def blacklist():

    role_filter = request.args.get('role')
    user_filter_id = request.args.get('user_id')

    # Lọc danh sách blacklist
    query = BlacklistEntry.query

    if role_filter == 'admin':
        query = query.join(User).filter(User.role == 'admin')
    elif role_filter == 'member':
        query = query.join(User).filter(User.role == 'member')

    if user_filter_id:
        query = query.filter(BlacklistEntry.created_by_id == int(user_filter_id))

    entries = query.order_by(BlacklistEntry.id.desc()).all()

    # Danh sách người đã từng tạo entry
    creators = (
        db.session.query(User)
        .join(BlacklistEntry, BlacklistEntry.created_by_id == User.id)
        .filter(User.role.in_(['admin', 'member']))
        .distinct()
        .all()
    )

    return render_template(
        'blacklist.html',
        entries=entries,
        all_users=creators,
        role_filter=role_filter,
        user_filter_id=user_filter_id,
        user=current_user
    )

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

@app.route('/fix_sequence')
def fix_sequence():
    from sqlalchemy import text
    db.session.execute(text("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users))"))
    db.session.commit()
    return "✅ Đã cập nhật sequence users_id_seq!"

@app.route("/game_history")
def game_history():
    from models import GameHistory, User, CharacterAbility
    games = GameHistory.query.order_by(GameHistory.created_at.desc()).all()
    users = User.query.all()
    chars = CharacterAbility.query.all()
    return render_template("game_history.html", games=games, users=users, chars=chars)

import random
from flask import request, redirect, url_for, flash

@app.route("/create_game", methods=["POST"])
@login_required
def create_game():

    from models import GameHistory, GamePlayer, db, CharacterAbility, User

    player_ids = request.form.getlist("players")
    char_ids = request.form.getlist("chars")

    if len(player_ids) != len(char_ids):
        flash("Số lượng người chơi và nhân vật phải bằng nhau", "danger")
        return redirect(url_for('game_history'))

    # Random pairing
    random.shuffle(char_ids)

    new_game = GameHistory(host_id=current_user.id)
    db.session.add(new_game)
    db.session.flush()  # để lấy id game mới

    for player_id, char_id in zip(player_ids, char_ids):
        p = GamePlayer(game_id=new_game.id, player_id=int(player_id), char_id=int(char_id))
        db.session.add(p)

    db.session.commit()
    flash("Tạo ván mới thành công!", "success")
    return redirect(url_for('game_history'))

@app.route("/day_off", methods=["GET", "POST"])
@login_required
def day_off():
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    if request.method == "POST":
        start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
        reason = request.form.get("reason", "")

        actual_user_id = user.id
        created_by = user.id

        # ✅ Nếu là admin thì được chọn người khác
        if user.role == 'admin' and request.form.get("user_id"):
            actual_user_id = int(request.form["user_id"])

        request_off = PlayerOffRequest(
            user_id=actual_user_id,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            created_by=created_by
        )
        db.session.add(request_off)
        db.session.commit()
        flash("Đã gửi yêu cầu xin nghỉ!", "success")
        return redirect(url_for("day_off"))

    # ✅ Dữ liệu để render form
    users = User.query.all() if user.role == 'admin' else []
    my_offs = PlayerOffRequest.query.filter_by(user_id=user.id).order_by(PlayerOffRequest.start_date.desc()).all()
    return render_template("day_off.html", users=users, my_offs=my_offs, current_user=user, user=user)

from datetime import datetime, timedelta
from sqlalchemy import func
from flask import render_template

@app.route("/frequency")
@login_required
def frequency():
    today = datetime.utcnow().date()

    # Lấy tất cả user
    users = User.query.all()

    # Lấy danh sách nghỉ (vẫn còn hiệu lực)
    current_offs = db.session.query(
        PlayerOffRequest.user_id,
        func.max(PlayerOffRequest.end_date).label("latest_end")
    ).filter(
        PlayerOffRequest.start_date <= today,
        PlayerOffRequest.end_date >= today
    ).group_by(PlayerOffRequest.user_id).all()

    off_dict = {user_id: latest_end for user_id, latest_end in current_offs}

    # Lấy số lần chơi và lần cuối tham gia từ bảng GamePlayer
    stats = db.session.query(
        GamePlayer.player_id,
        func.count(GamePlayer.id).label("play_count"),
        func.max(GameHistory.created_at).label("last_play")
    ).join(GameHistory, GamePlayer.game_id == GameHistory.id)\
     .group_by(GamePlayer.player_id).all()

    data = []

    # Tạo danh sách đã có số liệu
    handled_ids = set()

    for player_id, play_count, last_play in stats:
        user = User.query.get(player_id)
        if not user:
            continue

        # Nếu đang trong kỳ nghỉ, tính lần cuối từ end_date
        if player_id in off_dict:
            adjusted_last_play = max(last_play.date(), off_dict[player_id])
        else:
            adjusted_last_play = last_play.date()

        inactive = (today - adjusted_last_play).days > 7

        data.append({
            "user": user,
            "play_count": play_count,
            "last_play": adjusted_last_play,
            "inactive": inactive,
            "on_leave": player_id in off_dict
        })
        handled_ids.add(player_id)

    # Người chưa từng chơi
    for u in users:
        if u.id in handled_ids:
            continue

        # Nếu người này đang xin nghỉ
        if u.id in off_dict:
            adjusted_last_play = off_dict[u.id]
            inactive = (today - adjusted_last_play).days > 7
            data.append({
                "user": u,
                "play_count": 0,
                "last_play": adjusted_last_play,
                "inactive": inactive,
                "on_leave": True
            })
        else:
            # Không có ván nào và không xin nghỉ
            data.append({
                "user": u,
                "play_count": 0,
                "last_play": None,
                "inactive": True,
                "on_leave": False
            })

    return render_template("frequency.html", data=data)


print(f"📌 Flask app = {app}")
