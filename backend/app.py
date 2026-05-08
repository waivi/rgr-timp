from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)  # Разрешаем фронтенду общаться с нами

# --- Базы данных пока нет, храним всё в памяти (в будущем заменим на настоящую БД) ---

users = [
    {"id": 1, "name": "Охранник Сергей", "login": "security", "password": "123", "role": "security"},
    {"id": 2, "name": "Сантехник Петя", "login": "plumber", "password": "123", "role": "employee"},
    {"id": 3, "name": "Электрик Вася", "login": "electric", "password": "123", "role": "employee"},
    {"id": 4, "name": "Охранник Анна", "login": "security2", "password": "123", "role": "security"},
]

doors = [
    {"id": 1, "name": "Серверная 2 этаж", "description": "Стойки с оборудованием", "active": True},
    {"id": 2, "name": "Склад белья", "description": "Комната 104", "active": True},
    {"id": 3, "name": "Щитовая", "description": "Электрощитовая 1 этаж", "active": True},
    {"id": 4, "name": "Комната горничных", "description": "Инвентарь для уборки", "active": True},
]

access_keys = []  # Здесь будут храниться выданные коды

# ID для новых ключей
next_key_id = 1

# --- Вспомогательные функции ---

def generate_pin():
    """Генерирует случайный 4-значный код"""
    return f"{random.randint(0, 9999):04d}"

def find_user_by_id(user_id):
    for u in users:
        if u["id"] == user_id:
            return u
    return None

def find_door_by_id(door_id):
    for d in doors:
        if d["id"] == door_id:
            return d
    return None

# --- Эндпоинты (то что умеет делать наш сервер) ---

@app.route("/api/login", methods=["POST"])
def login():
    """Вход в систему"""
    data = request.get_json()
    login = data.get("login")
    password = data.get("password")
    
    for user in users:
        if user["login"] == login and user["password"] == password:
            return jsonify({
                "success": True,
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "role": user["role"]
                }
            })
    
    return jsonify({"success": False, "message": "Неверный логин или пароль"}), 401


@app.route("/api/security/doors", methods=["GET"])
def get_doors():
    """Получить список всех дверей (для охранника)"""
    return jsonify(doors)


@app.route("/api/security/users", methods=["GET"])
def get_users():
    """Получить список всех сотрудников (для охранника)"""
    # Возвращаем без паролей
    safe_users = [{"id": u["id"], "name": u["name"], "role": u["role"]} for u in users]
    return jsonify(safe_users)


@app.route("/api/security/keys/generate", methods=["POST"])
def generate_key():
    """Охранник создаёт новый код доступа"""
    global next_key_id
    data = request.get_json()
    user_id = data.get("userId")
    door_id = data.get("doorId")
    hours = data.get("hours", 2)  # По умолчанию на 2 часа
    
    user = find_user_by_id(user_id)
    door = find_door_by_id(door_id)
    
    if not user or not door:
        return jsonify({"success": False, "message": "Сотрудник или дверь не найдены"}), 400
    
    # Генерируем уникальный код
    pin = generate_pin()
    # Проверяем что такой код ещё не активен
    active_pins = [k["pin"] for k in access_keys if k["status"] == "active"]
    while pin in active_pins:
        pin = generate_pin()
    
    valid_until = datetime.now() + timedelta(hours=hours)
    
    new_key = {
        "id": next_key_id,
        "pin": pin,
        "userId": user_id,
        "userName": user["name"],
        "doorId": door_id,
        "doorName": door["name"],
        "createdAt": datetime.now().isoformat(),
        "validUntil": valid_until.isoformat(),
        "status": "active"
    }
    
    next_key_id += 1
    access_keys.append(new_key)
    
    return jsonify({"success": True, "key": new_key})


@app.route("/api/security/keys", methods=["GET"])
def get_all_keys():
    """Охранник видит все выданные ключи"""
    # Сортируем: сначала активные, потом по времени
    sorted_keys = sorted(access_keys, key=lambda k: (k["status"] != "active", k["validUntil"]))
    return jsonify(sorted_keys)


@app.route("/api/security/keys/<int:key_id>/revoke", methods=["POST"])
def revoke_key(key_id):
    """Отозвать ключ (деактивировать)"""
    for key in access_keys:
        if key["id"] == key_id:
            key["status"] = "revoked"
            return jsonify({"success": True, "message": "Ключ отозван"})
    return jsonify({"success": False, "message": "Ключ не найден"}), 404


@app.route("/api/security/statistics", methods=["GET"])
def get_statistics():
    """Статистика: сколько активных кодов на каждую дверь"""
    stats = []
    for door in doors:
        count = len([k for k in access_keys 
                     if k["doorId"] == door["id"] and k["status"] == "active"])
        stats.append({
            "doorId": door["id"],
            "doorName": door["name"],
            "activeKeys": count
        })
    return jsonify(stats)


@app.route("/api/employee/<int:user_id>/keys", methods=["GET"])
def get_my_keys(user_id):
    """Сотрудник видит свои активные коды"""
    my_keys = [k for k in access_keys 
               if k["userId"] == user_id and k["status"] == "active"]
    return jsonify(my_keys)


if __name__ == "__main__":
    print("Сервер запущен: http://localhost:5000")
    app.run(debug=True, port=5000)