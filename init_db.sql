\c rgr

DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS access_keys CASCADE;
DROP TABLE IF EXISTS doors CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS positions CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

CREATE TABLE roles (
    role_id     SERIAL          PRIMARY KEY,
    role_name   VARCHAR(50)     NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE positions (
    position_id SERIAL          PRIMARY KEY,
    name        VARCHAR(50)    NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE users (
    user_id         SERIAL          PRIMARY KEY,
    role_id         INT             NOT NULL REFERENCES roles(role_id),
    position_id     INT             REFERENCES positions(position_id),
    last_name       VARCHAR(30)     NOT NULL,
    first_name      VARCHAR(30)     NOT NULL,
    middle_name     VARCHAR(40)     NOT NULL,
    login           VARCHAR(35)     NOT NULL UNIQUE,
    password_hash   VARCHAR(225)    NOT NULL,
    phone           VARCHAR(12)     NOT NULL,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE TABLE doors (
    door_id         SERIAL          PRIMARY KEY,
    door_name       VARCHAR(100)    NOT NULL UNIQUE,
    description     TEXT,
    location        VARCHAR(50)     NOT NULL,
    floor           INT             NOT NULL CHECK (floor BETWEEN 0 AND 4),
    room_number     INT,
    category        VARCHAR(30)     NOT NULL,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE
);

CREATE TABLE access_keys (
    key_id          SERIAL          PRIMARY KEY,
    user_id         INT             NOT NULL REFERENCES users(user_id),
    door_id         INT             NOT NULL REFERENCES doors(door_id),
    issued_id       INT             NOT NULL REFERENCES users(user_id),
    pin_code        VARCHAR(10)     NOT NULL,
    status          VARCHAR(15)     NOT NULL DEFAULT 'active'
                                    CHECK (status IN ('active', 'expired', 'revoked')),
    valid_from      TIMESTAMP       NOT NULL DEFAULT NOW(),
    valid_until     TIMESTAMP       NOT NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_until_check CHECK (valid_until > valid_from)
);

CREATE TABLE audit_logs (
    log_id          SERIAL          PRIMARY KEY,
    user_id         INT             NOT NULL REFERENCES users(user_id),
    action          VARCHAR(40)     NOT NULL,
    entity_type     VARCHAR(10),
    entity_id       INT,
    details         TEXT,
    ip_address      VARCHAR(45),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE TABLE door_sessions (
    session_id      SERIAL          PRIMARY KEY,
    access_key_id   INT             NOT NULL UNIQUE REFERENCES access_keys(key_id),
    user_id         INT             NOT NULL REFERENCES users(user_id),
    door_id         INT             NOT NULL REFERENCES doors(door_id),
    entered_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_role ON users(role_id);
CREATE INDEX idx_users_position ON users(position_id);
CREATE INDEX idx_users_login ON users(login);
CREATE INDEX idx_access_keys_user ON access_keys(user_id);
CREATE INDEX idx_access_keys_door ON access_keys(door_id);
CREATE INDEX idx_access_keys_issued ON access_keys(issued_id);
CREATE INDEX idx_access_keys_status ON access_keys(status);
CREATE INDEX idx_access_keys_valid ON access_keys(valid_until);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_time ON audit_logs(created_at);
CREATE INDEX idx_door_sessions_key ON door_sessions(access_key_id);
CREATE INDEX idx_door_sessions_user ON door_sessions(user_id);
CREATE INDEX idx_door_sessions_door ON door_sessions(door_id);

-- Роли
INSERT INTO roles (role_name, description) VALUES 
    ('администратор', 'Администратор системы — полный доступ'),
    ('менеджер безопасности', 'Менеджер безопасности — выдача кодов, просмотр статистики'),
    ('сотрудник', 'Сотрудник — видит только свои коды');

-- Должности
INSERT INTO positions (name, description) VALUES 
    ('Системный администратор', 'Управляет системой и пользователями'),
    ('Менеджер безопасности', 'Выдаёт коды доступа, контролирует доступ'),
    ('Сантехник', 'Ремонт и обслуживание водопровода'),
    ('Электрик', 'Ремонт и обслуживание электросетей'),
    ('Горничная', 'Уборка номеров и помещений'),
    ('Техник слаботочных систем', 'Обслуживание серверных и сетей'),
    ('Завхоз', 'Заведующий хозяйством, склады'),
    ('Лифтёр', 'Обслуживание лифтового оборудования'),
    ('Уборщик тех помещений', 'Уборка тех. помещений');

-- Пользователи
-- Пароль везде "123"
-- Хеш bcrypt для "123": $2b$12$LJ3m4ys3LkBAh0X5wKPX8uGz2N5F3KL7wB8RQo1dHF0pVmS9XYZ1a
INSERT INTO users (role_id, position_id, last_name, first_name, middle_name, login, password_hash, phone) VALUES 
    -- Администратор (role_id=1)
    (1, 1, 'Админов', 'Виктор', 'Сергеевич', 'admin',
     '$2b$12$LJ3m4ys3LkBAh0X5wKPX8uGz2N5F3KL7wB8RQo1dHF0pVmS9XYZ1a',
     '89000000001'),
    
    -- Менеджеры безопасности (role_id=2)
    (2, 2, 'Охранников', 'Сергей', 'Петрович', 'security',
     '$2b$12$LJ3m4ys3LkBAh0X5wKPX8uGz2N5F3KL7wB8RQo1dHF0pVmS9XYZ1a',
     '89000000002'),
    (2, 2, 'Безопасникова', 'Анна', 'Ивановна', 'security2',
     '$2b$12$LJ3m4ys3LkBAh0X5wKPX8uGz2N5F3KL7wB8RQo1dHF0pVmS9XYZ1a',
     '89000000003'),
    
    -- Сотрудники (role_id=3)
    (3, 3, 'Сантехников', 'Пётр', 'Алексеевич', 'plumber',
     '$2b$12$LJ3m4ys3LkBAh0X5wKPX8uGz2N5F3KL7wB8RQo1dHF0pVmS9XYZ1a',
     '89000000004'),
    (3, 4, 'Электриков', 'Василий', 'Игоревич', 'electric',
     '$2b$12$LJ3m4ys3LkBAh0X5wKPX8uGz2N5F3KL7wB8RQo1dHF0pVmS9XYZ1a',
     '89000000005'),
    (3, 5, 'Горничная', 'Мария', 'Степановна', 'maid',
     '$2b$12$LJ3m4ys3LkBAh0X5wKPX8uGz2N5F3KL7wB8RQo1dHF0pVmS9XYZ1a',
     '89000000006'),
    (3, 6, 'Технический', 'Николай', 'Дмитриевич', 'tech',
     '$2b$12$LJ3m4ys3LkBAh0X5wKPX8uGz2N5F3KL7wB8RQo1dHF0pVmS9XYZ1a',
     '89000000007'),
    (3, 7, 'Завхозов', 'Иван', 'Петрович', 'manager',
     '$2b$12$LJ3m4ys3LkBAh0X5wKPX8uGz2N5F3KL7wB8RQo1dHF0pVmS9XYZ1a',
     '89000000008'),
    (3, 8, 'Лифтов', 'Андрей', 'Николаевич', 'lift',
     '$2b$12$LJ3m4ys3LkBAh0X5wKPX8uGz2N5F3KL7wB8RQo1dHF0pVmS9XYZ1a',
     '89000000009'),
    (3, 9, 'Уборщиков', 'Дмитрий', 'Сергеевич', 'cleaner',
     '$2b$12$LJ3m4ys3LkBAh0X5wKPX8uGz2N5F3KL7wB8RQo1dHF0pVmS9XYZ1a',
     '89000000010');

-- Системный пользователь для логирования автоматических действий
INSERT INTO users (role_id, position_id, last_name, first_name, middle_name, login, password_hash, phone) VALUES 
    (1, 1, 'Система', 'Автоматическая', '-', 'system',
     '$2b$12$LJ3m4ys3LkBAh0X5wKPX8uGz2N5F3KL7wB8RQo1dHF0pVmS9XYZ1a',
     '89000000000');

-- Помещения
INSERT INTO doors (door_name, description, location, floor, room_number, category) VALUES 
    ('Серверная 2 этаж', 'Основная серверная стойка, кондиционеры', 'Корпус А', 2, 201, 'server'),
    ('Серверная 3 этаж', 'Резервное оборудование', 'Корпус А', 3, 301, 'server'),
    ('Склад белья', 'Хранение белья и полотенец', 'Корпус А', 1, 104, 'storage'),
    ('Склад инвентаря', 'Дорогой инвентарь для уборки', 'Корпус Б', 1, 102, 'storage'),
    ('Щитовая 1 этаж', 'Электрощитовая главная', 'Корпус А', 1, 105, 'electrical'),
    ('Щитовая 2 этаж', 'Распределительный щит', 'Корпус А', 2, 205, 'electrical'),
    ('Комната горничных', 'Инвентарь и моющие средства', 'Корпус Б', 1, 101, 'staff'),
    ('Техническое помещение 4 этаж', 'Вентиляция и кондиционирование', 'Корпус А', 4, 401, 'staff');
