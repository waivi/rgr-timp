from app import app, db, User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

with app.app_context():
    # Получаем всех пользователей
    users = User.query.all()
    
    if not users:
        print("Нет пользователей в базе данных!")
    else:
        print(f"Найдено пользователей: {len(users)}")
        
        for user in users:
            # Устанавливаем пароль "123" для всех
            old_hash = user.password_hash
            user.password_hash = bcrypt.generate_password_hash("123").decode('utf-8')
            
            print(f"\nПользователь: {user.login}")
            print(f"Старый хэш: {old_hash[:50]}...")
            print(f"Новый хэш: {user.password_hash[:50]}...")
            
            # Проверяем сразу
            if bcrypt.check_password_hash(user.password_hash, "123"):
                print(f"✓ Пароль для {user.login} успешно обновлен")
            else:
                print(f"✗ Ошибка при обновлении пароля для {user.login}")
        
        # Сохраняем изменения
        db.session.commit()
        print("\n✓ Все пароли обновлены на '123'")
        
        # Дополнительная проверка
        print("\n=== Финальная проверка ===")
        for user in users:
            if bcrypt.check_password_hash(user.password_hash, "123"):
                print(f"✓ {user.login} - пароль работает")
            else:
                print(f"✗ {user.login} - пароль НЕ работает")
