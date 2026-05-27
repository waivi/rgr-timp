from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from functools import wraps
import jwt
import pytz
import random
import os
import re

# ==================== НАСТРОЙКИ ====================
app = Flask(__name__)
CORS(app)

# Секретный ключ для JWT (замени на случайную строку из 50+ символов)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'rgr-hotel-secret-key-change-in-production-2024')

# Часовой пояс Новосибирска
TIMEZONE = pytz.timezone('Asia/Novosibirsk')

def now():
    """Возвращает текущее время в Новосибирске"""
    return datetime.now(TIMEZONE)

# Строка подключения к PostgreSQL
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://hotel_admin:7912@localhost:5432/rgr'
)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ==================== МОДЕЛИ ====================

class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(55))
    users = db.relationship('User', backref='role_ref', lazy=True, foreign_keys='User.role_id')

    def to_dict(self):
        return {'id': self.role_id, 'name': self.role_name, 'description': self.description}


class Position(db.Model):
    __tablename__ = 'positions'
    position_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))
    users = db.relationship('User', backref='position_ref', lazy=True, foreign_keys='User.position_id')

    def to_dict(self):
        return {'id': self.position_id, 'name': self.name, 'description': self.description}


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.position_id'))
    last_name = db.Column(db.String(30), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    middle_name = db.Column(db.String(40), nullable=False)
    login = db.Column(db.String(35), unique=True, nullable=False)
    password_hash = db.Column(db.String(225), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=now)

    role = db.relationship('Role', foreign_keys=[role_id], lazy=True)
    position = db.relationship('Position', foreign_keys=[position_id], lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.user_id,
            'roleId': self.role_id,
            'roleName': self.role.role_name if self.role else None,
            'positionId': self.position_id,
            'positionName': self.position.name if self.position else None,
            'lastName': self.last_name,
            'firstName': self.first_name,
            'middleName': self.middle_name,
            'fullName': f"{self.last_name} {self.first_name} {self.middle_name}".strip(),
            'login': self.login,
            'phone': self.phone,
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

    def to_safe_dict(self):
        return {
            'id': self.user_id,
            'name': f"{self.last_name} {self.first_name}".strip(),
            'role': self.role.role_name if self.role else None,
            'roleId': self.role_id,
            'position': self.position.name if self.position else None,
            'positionId': self.position_id
        }


class Door(db.Model):
    __tablename__ = 'doors'
    door_id = db.Column(db.Integer, primary_key=True)
    door_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(100))
    location = db.Column(db.String(50), nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    room_number = db.Column(db.Integer)
    category = db.Column(db.String(30), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.door_id,
            'name': self.door_name,
            'description': self.description,
            'location': self.location,
            'floor': self.floor,
            'roomNumber': self.room_number,
            'category': self.category,
            'isActive': self.is_active
        }


class AccessKey(db.Model):
    __tablename__ = 'access_keys'
    key_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    door_id = db.Column(db.Integer, db.ForeignKey('doors.door_id'), nullable=False)
    issued_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(15), default='active', nullable=False)
    valid_from = db.Column(db.DateTime, default=now, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=now)

    recipient = db.relationship('User', foreign_keys=[user_id], lazy=True)
    issuer = db.relationship('User', foreign_keys=[issued_id], lazy=True)
    door = db.relationship('Door', backref='access_keys', lazy=True)

    def to_dict(self):
        return {
            'id': self.key_id,
            'pin': self.pin_code,
            'userId': self.user_id,
            'userName': f"{self.recipient.last_name} {self.recipient.first_name}".strip() if self.recipient else None,
            'userPosition': self.recipient.position.name if self.recipient and self.recipient.position else None,
            'doorId': self.door_id,
            'doorName': self.door.door_name if self.door else None,
            'doorLocation': self.door.location if self.door else None,
            'issuedById': self.issued_id,
            'issuedByName': f"{self.issuer.last_name} {self.issuer.first_name}".strip() if self.issuer else None,
            'status': self.status,
            'validFrom': self.valid_from.isoformat() if self.valid_from else None,
            'validUntil': self.valid_until.isoformat() if self.valid_until else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    action = db.Column(db.String(40), nullable=False)
    entity_type = db.Column(db.String(10))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=now)

    user = db.relationship('User', backref='audit_logs', lazy=True)

    def to_dict(self):
        return {
            'id': self.log_id,
            'userId': self.user_id,
            'userName': f"{self.user.last_name} {self.user.first_name}".strip() if self.user else 'Система',
            'action': self.action,
            'entityType': self.entity_type,
            'entityId': self.entity_id,
            'details': self.details,
            'ipAddress': self.ip_address,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class DoorSession(db.Model):
    __tablename__ = 'door_sessions'
    session_id = db.Column(db.Integer, primary_key=True)
    access_key_id = db.Column(db.Integer, db.ForeignKey('access_keys.key_id'), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    door_id = db.Column(db.Integer, db.ForeignKey('doors.door_id'), nullable=False)
    entered_at = db.Column(db.DateTime, default=now, nullable=False)

    access_key = db.relationship('AccessKey', backref='session', lazy=True, uselist=False)
    user = db.relationship('User', lazy=True)
    door = db.relationship('Door', lazy=True)

    def to_dict(self):
        return {
            'sessionId': self.session_id,
            'accessKeyId': self.access_key_id,
            'pin': self.access_key.pin_code if self.access_key else None,
            'userId': self.user_id,
            'userName': f"{self.user.last_name} {self.user.first_name}".strip() if self.user else None,
            'userPosition': self.user.position.name if self.user and self.user.position else None,
            'doorId': self.door_id,
            'doorName': self.door.door_name if self.door else None,
            'doorLocation': self.door.location if self.door else None,
            'enteredAt': self.entered_at.isoformat() if self.entered_at else None
        }


# ==================== RATE LIMIT (ЗАЩИТА ОТ ПЕРЕБОРА) ====================

# Простое хранилище в памяти (для продакшена — Redis)
from collections import defaultdict
import time

rate_limit_store = defaultdict(list)

def rate_limit(max_attempts=5, window_seconds=60):
    """
    Ограничивает количество запросов с одного IP.
    max_attempts — максимум запросов за window_seconds секунд.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ip = request.remote_addr
            now_ts = time.time()
            # Удаляем старые записи
            rate_limit_store[ip] = [t for t in rate_limit_store[ip] if now_ts - t < window_seconds]
            
            if len(rate_limit_store[ip]) >= max_attempts:
                return jsonify({
                    "success": False,
                    "message": f"Слишком много запросов. Попробуйте через {window_seconds} секунд.",
                    "code": 429
                }), 429
            
            rate_limit_store[ip].append(now_ts)
            return f(*args, **kwargs)
        return decorated
    return decorator


# ==================== JWT ТОКЕНЫ ====================

def generate_token(user_id, role):
    """Создаёт JWT токен (хранится на клиенте, не на сервере)"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=8),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def verify_token(token):
    """Проверяет JWT токен. Возвращает payload или None."""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Декоратор — требует JWT токен в заголовке Authorization"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"success": False, "message": "Требуется авторизация. Передайте токен в заголовке Authorization.", "code": 401}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({"success": False, "message": "Токен недействителен или истёк. Войдите заново.", "code": 401}), 401
        
        request.current_user_id = payload['user_id']
        request.current_user_role = payload['role']
        return f(*args, **kwargs)
    return decorated


def require_role(role_name):
    """Декоратор — требует определённую роль"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.current_user_role != role_name and request.current_user_role != 'администратор':
                return jsonify({"success": False, "message": f"Доступ запрещён. Требуется роль: {role_name}", "code": 403}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

SYSTEM_USER_ID = 11

def generate_pin(length=4):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def get_unique_pin():
    while True:
        pin = generate_pin()
        exists = AccessKey.query.filter_by(pin_code=pin, status='active').first()
        if not exists:
            return pin

def log_action(user_id, action, entity_type=None, entity_id=None, details=None, ip_address=None):
    import json
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=json.dumps(details, ensure_ascii=False) if details else None,
        ip_address=ip_address
    )
    db.session.add(log)
    db.session.commit()

def expire_old_keys():
    current_time = now()
    expired = AccessKey.query.filter(
        AccessKey.status == 'active',
        AccessKey.valid_until <= current_time
    ).all()
    for key in expired:
        key.status = 'expired'
        log_action(SYSTEM_USER_ID, 'KEY_EXPIRED', entity_type='KEY', entity_id=key.key_id,
                   details={'pin': key.pin_code, 'userId': key.user_id, 'doorId': key.door_id,
                            'validUntil': key.valid_until.isoformat(), 'reason': 'Автоматическое истечение срока'},
                   ip_address='127.0.0.1')
    if expired:
        db.session.commit()

def can_enter_door(pin_code):
    key = AccessKey.query.filter_by(pin_code=pin_code, status='active').first()
    if not key:
        return False, "Неверный PIN или ключ недействителен"

    user = User.query.get(key.user_id)
    if not user or not user.is_active:
        key.status = 'revoked'
        db.session.commit()
        return False, "Ваша учётная запись заблокирована. Ключ аннулирован"

    key_time = key.valid_until
    if key_time.tzinfo is None:
        key_time = TIMEZONE.localize(key_time)
    if key_time <= now():
        key.status = 'expired'
        db.session.commit()
        return False, "Ключ не работает"
    

    existing_session = DoorSession.query.filter_by(access_key_id=key.key_id).first()
    if existing_session:
        return False, f"По этому PIN уже вошли в помещение (внутри: {existing_session.user.last_name} {existing_session.user.first_name})"
    return True, key


def validate_password(password):
    """Проверяет пароль: минимум 8 символов, хотя бы одна буква"""
    if len(password) < 8:
        return False, "Пароль должен быть не менее 8 символов"
    if not re.search(r'[a-zA-Zа-яА-Я]', password):
        return False, "Пароль должен содержать хотя бы одну букву"
    return True, ""


# ==================== ЭНДПОИНТЫ ====================

# --- Аутентификация (открытый, но с rate limit) ---

@app.route("/api/login", methods=["POST"])
@rate_limit(max_attempts=5, window_seconds=60)  # 5 попыток в минуту
def login():
    """Вход в систему. Возвращает JWT токен."""
    data = request.get_json()
    login = data.get('login', '').strip()
    password = data.get('password', '')

    if not login or not password:
        return jsonify({"success": False, "message": "Логин и пароль обязательны"}), 400

    user = User.query.filter_by(login=login, is_active=True).first()

    if user and user.check_password(password):
        token = generate_token(user.user_id, user.role.role_name)
        log_action(user.user_id, 'LOGIN', ip_address=request.remote_addr)
        return jsonify({
            "success": True,
            "token": token,
            "user": user.to_safe_dict()
        })

    return jsonify({"success": False, "message": "Неверный логин или пароль"}), 401


# --- Общие эндпоинты (открытые) ---

@app.route("/api/doors", methods=["GET"])
def get_doors():
    """Список активных дверей (открытый)"""
    doors = Door.query.filter_by(is_active=True).all()
    return jsonify([d.to_dict() for d in doors])


# --- Симуляция двери (открытые) ---

@app.route("/api/door/enter", methods=["POST"])
@rate_limit(max_attempts=10, window_seconds=60)
def door_enter():
    """Войти в помещение по PIN"""
    data = request.get_json()
    pin = data.get('pin', '').strip()

    if not pin or len(pin) != 4 or not pin.isdigit():
        return jsonify({"success": False, "message": "Введите 4-значный PIN"}), 400

    can_enter, result = can_enter_door(pin)

    if not can_enter:
        key = AccessKey.query.filter_by(pin_code=pin).first()
        log_action(key.user_id if key else SYSTEM_USER_ID, 'ENTER_DOOR_FAILED',
                   entity_type='KEY', entity_id=key.key_id if key else None,
                   details={'pin': pin, 'reason': result, 'success': False},
                   ip_address=request.remote_addr)
        return jsonify({"success": False, "message": result}), 403

    key = result
    session = DoorSession(access_key_id=key.key_id, user_id=key.user_id, door_id=key.door_id)
    db.session.add(session)
    db.session.commit()

    log_action(key.user_id, 'ENTER_DOOR', entity_type='KEY', entity_id=key.key_id,
               details={'pin': key.pin_code, 'doorName': key.door.door_name,
                        'doorLocation': key.door.location, 'success': True},
               ip_address=request.remote_addr)

    return jsonify({"success": True, "message": f"Дверь открыта! Вы вошли в: {key.door.door_name}",
                    "session": session.to_dict()})


@app.route("/api/door/exit", methods=["POST"])
def door_exit():
    """Выйти из помещения по PIN"""
    data = request.get_json()
    pin = data.get('pin', '').strip()

    if not pin or len(pin) != 4 or not pin.isdigit():
        return jsonify({"success": False, "message": "Введите 4-значный PIN"}), 400

    key = AccessKey.query.filter_by(pin_code=pin).first()
    if not key:
        return jsonify({"success": False, "message": "Ключ с таким PIN не найден"}), 404

    session = DoorSession.query.filter_by(access_key_id=key.key_id).first()
    if not session:
        return jsonify({"success": False, "message": "Вы не находитесь в помещении"}), 400

    door_name = session.door.door_name if session.door else "Неизвестно"
    db.session.delete(session)
    db.session.commit()

    log_action(key.user_id, 'EXIT_DOOR', entity_type='KEY', entity_id=key.key_id,
               details={'pin': key.pin_code, 'doorName': door_name},
               ip_address=request.remote_addr)

    return jsonify({"success": True, "message": f"Вы вышли из: {door_name}"})


@app.route("/api/door/status", methods=["GET"])
def door_status():
    """Статус занятых помещений"""
    sessions = DoorSession.query.all()
    return jsonify([s.to_dict() for s in sessions])


# --- Эндпоинты сотрудника (защищённые) ---

@app.route("/api/employee/keys", methods=["GET"])
@require_auth
def get_my_keys():
    """Сотрудник видит свои активные коды"""
    user_id = request.current_user_id
    keys = AccessKey.query.filter_by(user_id=user_id, status='active').order_by(AccessKey.valid_until).all()
    return jsonify([k.to_dict() for k in keys])


# --- Эндпоинты менеджера безопасности (защищённые) ---

@app.route("/api/security/users", methods=["GET"])
@require_auth
@require_role('менеджер безопасности')
def get_employees():
    """Список сотрудников для выдачи ключей"""
    users = User.query.filter_by(is_active=True).join(Role).filter(Role.role_name == 'сотрудник').all()
    return jsonify([u.to_dict() for u in users])


@app.route("/api/security/keys/generate", methods=["POST"])
@require_auth
@require_role('менеджер безопасности')
def generate_key():
    """Создать новый код доступа"""
    data = request.get_json()
    user_id = data.get('userId')
    door_id = data.get('doorId')
    hours = data.get('hours', 2)
    issued_by = request.current_user_id

    user = User.query.get(user_id)
    door = Door.query.get(door_id)

    if not user or not door:
        return jsonify({"success": False, "message": "Сотрудник или дверь не найдены"}), 400
    if not door.is_active:
        return jsonify({"success": False, "message": "Дверь не активна"}), 400

    pin = get_unique_pin()
    current_time = now()
    valid_until = current_time + timedelta(hours=hours)

    key = AccessKey(user_id=user_id, door_id=door_id, issued_id=issued_by,
                    pin_code=pin, status='active', valid_from=current_time, valid_until=valid_until)
    db.session.add(key)
    db.session.commit()

    log_action(issued_by, 'CREATE_KEY', entity_type='KEY', entity_id=key.key_id,
               details={'pin': pin, 'userName': f"{user.last_name} {user.first_name}", 'doorName': door.door_name},
               ip_address=request.remote_addr)

    return jsonify({"success": True, "key": key.to_dict()})


@app.route("/api/security/keys", methods=["GET"])
@require_auth
@require_role('менеджер безопасности')
def get_all_keys():
    """Все ключи"""
    expire_old_keys()
    keys = AccessKey.query.order_by(AccessKey.status == 'active', AccessKey.valid_until.desc()).all()
    return jsonify([k.to_dict() for k in keys])


@app.route("/api/security/keys/<int:key_id>/revoke", methods=["POST"])
@require_auth
@require_role('менеджер безопасности')
def revoke_key(key_id):
    """Отозвать ключ"""
    data = request.get_json() or {}
    reason = data.get('reason', '')
    revoked_by = request.current_user_id

    key = AccessKey.query.get(key_id)
    if not key:
        return jsonify({"success": False, "message": "Ключ не найден"}), 404
    if key.status != 'active':
        return jsonify({"success": False, "message": f"Ключ уже {key.status}"}), 400

    key.status = 'revoked'
    db.session.commit()

    log_action(revoked_by, 'REVOKE_KEY', entity_type='KEY', entity_id=key.key_id,
               details={'reason': reason, 'pin': key.pin_code}, ip_address=request.remote_addr)
    return jsonify({"success": True, "message": "Ключ отозван"})


@app.route("/api/security/statistics", methods=["GET"])
@require_auth
@require_role('менеджер безопасности')
def get_statistics():
    """Статистика по дверям"""
    doors = Door.query.filter_by(is_active=True).all()
    stats = []
    for door in doors:
        count = AccessKey.query.filter_by(door_id=door.door_id, status='active').count()
        stats.append({'doorId': door.door_id, 'doorName': door.door_name,
                      'doorCategory': door.category, 'activeKeys': count})
    return jsonify(stats)


# --- Эндпоинты администратора (защищённые) ---

@app.route("/api/admin/users", methods=["GET"])
@require_auth
@require_role('администратор')
def admin_get_users():
    """Список всех пользователей"""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])


@app.route("/api/admin/users", methods=["POST"])
@require_auth
@require_role('администратор')
def admin_create_user():
    """Создать пользователя с валидацией"""
    data = request.get_json()

    # Обязательные поля
    required = ['login', 'password', 'lastName', 'firstName', 'roleId']
    for field in required:
        if field not in data or not str(data[field]).strip():
            return jsonify({"success": False, "message": f"Поле '{field}' обязательно"}), 400

    login = data['login'].strip()
    password = data['password']
    first_name = data['firstName'].strip()
    last_name = data['lastName'].strip()

    # Валидация логина
    if len(login) < 3 or len(login) > 35:
        return jsonify({"success": False, "message": "Логин должен быть от 3 до 35 символов"}), 400
    if not re.match(r'^[a-zA-Z0-9_]+$', login):
        return jsonify({"success": False, "message": "Логин должен содержать только латинские буквы, цифры и _"}), 400

    # Валидация пароля
    valid, msg = validate_password(password)
    if not valid:
        return jsonify({"success": False, "message": msg}), 400

    # Валидация имени и фамилии
    if len(first_name) < 1 or len(first_name) > 30:
        return jsonify({"success": False, "message": "Имя должно быть от 1 до 30 символов"}), 400
    if len(last_name) < 1 or len(last_name) > 30:
        return jsonify({"success": False, "message": "Фамилия должна быть от 1 до 30 символов"}), 400

    # Валидация роли
    role = Role.query.get(data['roleId'])
    if not role:
        return jsonify({"success": False, "message": "Указанная роль не существует"}), 400

    # Уникальность логина
    if User.query.filter_by(login=login).first():
        return jsonify({"success": False, "message": "Логин уже занят"}), 409

    # Валидация телефона
    phone = data.get('phone', '').strip()
    if phone and not re.match(r'^\+?[0-9]{10,12}$', phone):
        return jsonify({"success": False, "message": "Некорректный формат телефона (10-12 цифр)"}), 400

    user = User(
        role_id=data['roleId'],
        position_id=data.get('positionId'),
        last_name=last_name,
        first_name=first_name,
        middle_name=data.get('middleName', ''),
        login=login,
        phone=phone if phone else '',
        is_active=True
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    log_action(request.current_user_id, 'CREATE_USER', entity_type='USER',
               entity_id=user.user_id,
               details={'login': user.login, 'role': user.role.role_name},
               ip_address=request.remote_addr)

    return jsonify({"success": True, "user": user.to_dict()})


@app.route("/api/admin/users/<int:user_id>", methods=["PUT"])
@require_auth
@require_role('администратор')
def admin_update_user(user_id):
    """Редактировать пользователя"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "Пользователь не найден"}), 404

    data = request.get_json()
    if 'lastName' in data: user.last_name = data['lastName']
    if 'firstName' in data: user.first_name = data['firstName']
    if 'middleName' in data: user.middle_name = data['middleName']
    if 'roleId' in data: user.role_id = data['roleId']
    if 'positionId' in data: user.position_id = data['positionId']
    if 'phone' in data: user.phone = data['phone']
    if 'password' in data and data['password']:
        valid, msg = validate_password(data['password'])
        if not valid:
            return jsonify({"success": False, "message": msg}), 400
        user.set_password(data['password'])
    if 'isActive' in data:
        user.is_active = data['isActive']
        if not data['isActive']:
            log_action(request.current_user_id, 'BLOCK_USER', entity_type='USER',
                       entity_id=user.user_id, ip_address=request.remote_addr)

    db.session.commit()
    return jsonify({"success": True, "user": user.to_dict()})


@app.route("/api/admin/logs", methods=["GET"])
@require_auth
@require_role('администратор')
def admin_get_logs():
    """Журнал действий"""
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(500).all()
    return jsonify([log.to_dict() for log in logs])


@app.route("/api/admin/statistics", methods=["GET"])
@require_auth
@require_role('администратор')
def admin_get_all_stats():
    """Общая статистика"""
    total_users = User.query.filter_by(is_active=True).count()
    total_keys_active = AccessKey.query.filter_by(status='active').count()
    total_keys_today = AccessKey.query.filter(
        AccessKey.created_at >= now().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    return jsonify({'totalUsers': total_users, 'totalActiveKeys': total_keys_active, 'totalKeysToday': total_keys_today})


@app.route("/api/admin/positions", methods=["GET"])
@require_auth
def get_positions():
    """Список должностей"""
    positions = Position.query.all()
    return jsonify([p.to_dict() for p in positions])


@app.route("/api/admin/roles", methods=["GET"])
@require_auth
def get_roles():
    """Список ролей"""
    roles = Role.query.all()
    return jsonify([r.to_dict() for r in roles])


# ==================== ОБРАБОТЧИКИ ОШИБОК ====================

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "message": "Неверный запрос", "code": 400}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"success": False, "message": "Требуется авторизация", "code": 401}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({"success": False, "message": "Доступ запрещён", "code": 403}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "message": "Ресурс не найден", "code": 404}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"success": False, "message": "Метод не поддерживается", "code": 405}), 405

@app.errorhandler(409)
def conflict(error):
    return jsonify({"success": False, "message": "Конфликт данных", "code": 409}), 409

@app.errorhandler(429)
def too_many_requests(error):
    return jsonify({"success": False, "message": "Слишком много запросов. Попробуйте позже.", "code": 429}), 429

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "message": "Внутренняя ошибка сервера", "code": 500}), 500


# ==================== ЗАПУСК ====================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print("Сервер запущен: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)