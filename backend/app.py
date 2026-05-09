from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import random
import os

# ==================== НАСТРОЙКИ ====================
app = Flask(__name__)
CORS(app)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role = db.relationship('Role', foreign_keys=[role_id], lazy=True)
    position = db.relationship('Position', foreign_keys=[position_id], lazy=True)

    def set_password(self, password):
        """Хеширует пароль (хеширование происходит ЗДЕСЬ, в коде)"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Проверяет пароль"""
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
    valid_from = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

SYSTEM_USER_ID = 11  # ID системного пользователя (создаётся в init_db.sql)

def generate_pin(length=4):
    """Генерирует случайный PIN-код"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def get_unique_pin():
    """Генерирует уникальный PIN (не активный сейчас)"""
    while True:
        pin = generate_pin()
        exists = AccessKey.query.filter_by(pin_code=pin, status='active').first()
        if not exists:
            return pin

def log_action(user_id, action, entity_type=None, entity_id=None, details=None, ip_address=None):
    """Записывает действие в аудит"""
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
    """Автоматически проставляет статус expired для просроченных ключей и логирует"""
    now = datetime.utcnow()
    expired = AccessKey.query.filter(
        AccessKey.status == 'active',
        AccessKey.valid_until <= now
    ).all()

    for key in expired:
        key.status = 'expired'
        log_action(
            SYSTEM_USER_ID,
            'KEY_EXPIRED',
            entity_type='KEY',
            entity_id=key.key_id,
            details={
                'pin': key.pin_code,
                'userId': key.user_id,
                'doorId': key.door_id,
                'validUntil': key.valid_until.isoformat(),
                'reason': 'Автоматическое истечение срока'
            },
            ip_address='127.0.0.1'
        )

    if expired:
        db.session.commit()

# ==================== ЭНДПОИНТЫ ====================

# --- Аутентификация ---

@app.route("/api/login", methods=["POST"])
def login():
    """Вход в систему"""
    data = request.get_json()
    login = data.get('login', '').strip()
    password = data.get('password', '')

    if not login or not password:
        return jsonify({"success": False, "message": "Логин и пароль обязательны"}), 400

    user = User.query.filter_by(login=login, is_active=True).first()

    if user and user.check_password(password):
        log_action(user.user_id, 'LOGIN', ip_address=request.remote_addr)
        return jsonify({
            "success": True,
            "user": user.to_safe_dict()
        })

    return jsonify({"success": False, "message": "Неверный логин или пароль"}), 401


# --- Общие эндпоинты ---

@app.route("/api/doors", methods=["GET"])
def get_doors():
    """Получить список всех активных дверей"""
    doors = Door.query.filter_by(is_active=True).all()
    return jsonify([d.to_dict() for d in doors])


# --- Эндпоинты сотрудника ---

@app.route("/api/employee/<int:user_id>/keys", methods=["GET"])
def get_my_keys(user_id):
    """Сотрудник видит свои активные коды"""
    keys = AccessKey.query.filter_by(
        user_id=user_id,
        status='active'
    ).order_by(AccessKey.valid_until).all()
    return jsonify([k.to_dict() for k in keys])


# --- Эндпоинты менеджера безопасности ---

@app.route("/api/security/users", methods=["GET"])
def get_employees():
    """Список сотрудников (employee) для выдачи ключей"""
    users = User.query.filter_by(is_active=True).join(Role).filter(
        Role.role_name == 'сотрудник'
    ).all()
    return jsonify([u.to_dict() for u in users])


@app.route("/api/security/keys/generate", methods=["POST"])
def generate_key():
    """Менеджер безопасности создаёт новый код"""
    data = request.get_json()
    user_id = data.get('userId')
    door_id = data.get('doorId')
    hours = data.get('hours', 2)
    issued_by = data.get('issuedBy')

    user = User.query.get(user_id)
    door = Door.query.get(door_id)

    if not user or not door:
        return jsonify({"success": False, "message": "Сотрудник или дверь не найдены"}), 400

    if not door.is_active:
        return jsonify({"success": False, "message": "Дверь не активна"}), 400

    # Проверяем что issued_by — менеджер безопасности
    issuer = User.query.get(issued_by)
    if not issuer or issuer.role.role_name not in ('менеджер безопасности', 'администратор'):
        return jsonify({"success": False, "message": "Недостаточно прав"}), 403

    pin = get_unique_pin()
    valid_until = datetime.utcnow() + timedelta(hours=hours)

    key = AccessKey(
        user_id=user_id,
        door_id=door_id,
        issued_id=issued_by,
        pin_code=pin,
        status='active',
        valid_from=datetime.utcnow(),
        valid_until=valid_until
    )

    db.session.add(key)
    db.session.commit()

    log_action(issued_by, 'CREATE_KEY', entity_type='KEY', entity_id=key.key_id,
               details={'pin': pin,
                        'userName': f"{user.last_name} {user.first_name}",
                        'doorName': door.door_name},
               ip_address=request.remote_addr)

    return jsonify({"success": True, "key": key.to_dict()})


@app.route("/api/security/keys", methods=["GET"])
def get_all_keys():
    """Менеджер видит все ключи"""
    expire_old_keys()  # Сначала обновляем просроченные
    keys = AccessKey.query.order_by(
        AccessKey.status == 'active',
        AccessKey.valid_until.desc()
    ).all()
    return jsonify([k.to_dict() for k in keys])


@app.route("/api/security/keys/<int:key_id>/revoke", methods=["POST"])
def revoke_key(key_id):
    """Отозвать ключ"""
    data = request.get_json() or {}
    reason = data.get('reason', '')
    revoked_by = data.get('revokedBy')

    key = AccessKey.query.get(key_id)
    if not key:
        return jsonify({"success": False, "message": "Ключ не найден"}), 404

    if key.status != 'active':
        return jsonify({"success": False, "message": f"Ключ уже {key.status}"}), 400

    key.status = 'revoked'
    db.session.commit()

    log_action(revoked_by, 'REVOKE_KEY', entity_type='KEY', entity_id=key.key_id,
               details={'reason': reason, 'pin': key.pin_code},
               ip_address=request.remote_addr)

    return jsonify({"success": True, "message": "Ключ отозван"})


@app.route("/api/security/statistics", methods=["GET"])
def get_statistics():
    """Статистика по дверям"""
    doors = Door.query.filter_by(is_active=True).all()
    stats = []
    for door in doors:
        count = AccessKey.query.filter_by(door_id=door.door_id, status='active').count()
        stats.append({
            'doorId': door.door_id,
            'doorName': door.door_name,
            'doorCategory': door.category,
            'activeKeys': count
        })
    return jsonify(stats)


# --- Эндпоинты администратора ---

@app.route("/api/admin/users", methods=["GET"])
def admin_get_users():
    """Админ видит всех пользователей"""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])


@app.route("/api/admin/users", methods=["POST"])
def admin_create_user():
    """Админ создаёт нового пользователя"""
    data = request.get_json()

    required = ['login', 'password', 'lastName', 'firstName', 'roleId']
    for field in required:
        if field not in data:
            return jsonify({"success": False, "message": f"Поле {field} обязательно"}), 400

    if User.query.filter_by(login=data['login']).first():
        return jsonify({"success": False, "message": "Логин уже занят"}), 400

    user = User(
        role_id=data['roleId'],
        position_id=data.get('positionId'),
        last_name=data['lastName'],
        first_name=data['firstName'],
        middle_name=data.get('middleName', ''),
        login=data['login'],
        phone=data.get('phone', ''),
        is_active=True
    )
    user.set_password(data['password'])  # ХЕШИРУЕТСЯ ЗДЕСЬ

    db.session.add(user)
    db.session.commit()

    log_action(data.get('createdBy'), 'CREATE_USER', entity_type='USER',
               entity_id=user.user_id,
               details={'login': user.login, 'role': user.role.role_name},
               ip_address=request.remote_addr)

    return jsonify({"success": True, "user": user.to_dict()})


@app.route("/api/admin/users/<int:user_id>", methods=["PUT"])
def admin_update_user(user_id):
    """Админ редактирует пользователя"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "Пользователь не найден"}), 404

    data = request.get_json()
    if 'lastName' in data:
        user.last_name = data['lastName']
    if 'firstName' in data:
        user.first_name = data['firstName']
    if 'middleName' in data:
        user.middle_name = data['middleName']
    if 'roleId' in data:
        user.role_id = data['roleId']
    if 'positionId' in data:
        user.position_id = data['positionId']
    if 'phone' in data:
        user.phone = data['phone']
    if 'password' in data and data['password']:
        user.set_password(data['password'])  # ХЕШИРУЕТСЯ ЗДЕСЬ
    if 'isActive' in data:
        user.is_active = data['isActive']
        if not data['isActive']:
            log_action(data.get('updatedBy'), 'BLOCK_USER',
                       entity_type='USER', entity_id=user.user_id,
                       ip_address=request.remote_addr)

    db.session.commit()
    return jsonify({"success": True, "user": user.to_dict()})


@app.route("/api/admin/logs", methods=["GET"])
def admin_get_logs():
    """Админ видит логи"""
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(500).all()
    return jsonify([log.to_dict() for log in logs])


@app.route("/api/admin/statistics", methods=["GET"])
def admin_get_all_stats():
    """Админ видит общую статистику"""
    total_users = User.query.filter_by(is_active=True).count()
    total_keys_active = AccessKey.query.filter_by(status='active').count()
    total_keys_today = AccessKey.query.filter(
        AccessKey.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).count()

    return jsonify({
        'totalUsers': total_users,
        'totalActiveKeys': total_keys_active,
        'totalKeysToday': total_keys_today
    })


@app.route("/api/admin/positions", methods=["GET"])
def get_positions():
    """Список должностей"""
    positions = Position.query.all()
    return jsonify([p.to_dict() for p in positions])


@app.route("/api/admin/roles", methods=["GET"])
def get_roles():
    """Список ролей"""
    roles = Role.query.all()
    return jsonify([r.to_dict() for r in roles])


# ==================== ЗАПУСК ====================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Создаст таблицы только если их нет
    print("Сервер запущен: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)