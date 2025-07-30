from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from database import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='member')
    points = db.Column(db.Integer, default=0)
    assigned_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    death_count = db.Column(db.Integer, default=0)
    has_kim_bai = db.Column(db.Boolean, default=False)
    # Thêm:
    hosted_games = db.relationship('GameHistory', backref='host', lazy=True, foreign_keys='GameHistory.host_id')
    played_games = db.relationship('GamePlayer', backref='player_info', lazy=True, foreign_keys='GamePlayer.player_id')
    theme = db.Column(db.String(50), nullable=True, default='default')


class MemberID(db.Model):
    __tablename__ = 'member_ids'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(db.String(100), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    used_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PointLog(db.Model):
    __tablename__ = 'point_logs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    points_change = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BlacklistEntry(db.Model):
    __tablename__ = 'blacklist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    facebook_link = db.Column(db.String(500))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.relationship('User', backref='blacklist_entries')

class CharacterAbility(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    faction = db.Column(db.String(100), nullable=False)
    order_in_faction = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class KimBaiLog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class GameHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    host_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    players = db.relationship('GamePlayer', backref='game', cascade="all, delete", lazy=True)
    notes = db.Column(db.Text, default='')
    tags = db.Column(db.String(255), default='')
    is_public = db.Column(db.Boolean, default=False)

class GamePlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game_history.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="SET NULL"), nullable=True)
    char_id = db.Column(db.Integer, db.ForeignKey('character_ability.id'))

    player = db.relationship('User', foreign_keys=[player_id], overlaps="player_info,played_games")
    char = db.relationship('CharacterAbility', foreign_keys=[char_id])

class PlayerOffRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    reason = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], backref='off_requests')
    creator = db.relationship('User', foreign_keys=[created_by])

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(255), nullable=False)
    detail = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='activity_logs')
