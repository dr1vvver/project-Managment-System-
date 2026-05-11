import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "users.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Таблицы создаются только если их нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            phone TEXT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            inn TEXT,
            email TEXT,
            rating REAL DEFAULT 0,
            created_date TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rating_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER NOT NULL,
            old_rating REAL,
            new_rating REAL,
            changed_by INTEGER NOT NULL,
            change_date TEXT NOT NULL,
            reason TEXT
        )
    ''')
    
    # Добавляем тестовые данные ТОЛЬКО если таблица пустая
    cursor.execute("SELECT COUNT(*) FROM profiles")
    if cursor.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        test_data = [
            ("ИП 'Иванов'", "89002223344", "partner2", hash_password("partner123"), "partner", "7701234568", "partner2@mail.ru", 4.8, now),
            ("Администратор", "", "admin", hash_password("admin123"), "admin", "", "", 0, now),
            ("Менеджер Петров", "89004445566", "manager", hash_password("manager123"), "manager", "", "", 0, now),
        ]
        cursor.executemany('''
            INSERT INTO profiles (fio, phone, login, password, role, inn, email, rating, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_data)
        conn.commit()
        print("База данных пользователей создана и заполнена")
    else:
        print("База данных пользователей уже существует, данные сохранены")
    
    conn.close()


def verify_user(login, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute("SELECT role, id, fio, rating FROM profiles WHERE login = ? AND password = ?", (login, hashed))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        print(f"VERIFY: {login} -> role={result[0]}, id={result[1]}, name={result[2]}, rating={result[3]}")
        return True, result[0], result[1], result[2], result[3]
    print(f"VERIFY: {login} -> НЕ НАЙДЕН")
    return False, None, None, None, None

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fio, role, rating FROM profiles WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else ("Пользователь", "user", 0)

def get_all_partners():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, fio, inn, phone, email, rating, created_date FROM profiles WHERE role = 'partner' ORDER BY fio")
    data = cursor.fetchall()
    conn.close()
    return data

def get_partner_by_id(partner_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, fio, inn, phone, email, rating FROM profiles WHERE id = ? AND role = 'partner'", (partner_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def add_partner(fio, phone, login, password, inn, email, rating=0):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed = hash_password(password)
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute('''
            INSERT INTO profiles (fio, phone, login, password, role, inn, email, rating, created_date)
            VALUES (?, ?, ?, ?, 'partner', ?, ?, ?, ?)
        ''', (fio, phone, login, hashed, inn, email, rating, now))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False
    finally:
        conn.close()

def update_partner_rating(partner_id, new_rating, changed_by, reason=""):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT rating FROM profiles WHERE id = ?", (partner_id,))
    old_rating = cursor.fetchone()
    if not old_rating:
        conn.close()
        return False
    old_rating = old_rating[0]
    
    cursor.execute("UPDATE profiles SET rating = ? WHERE id = ?", (new_rating, partner_id))
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute('''
        INSERT INTO rating_history (partner_id, old_rating, new_rating, changed_by, change_date, reason)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (partner_id, old_rating, new_rating, changed_by, now, reason))
    
    conn.commit()
    conn.close()
    return True

def get_rating_history(partner_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT rh.old_rating, rh.new_rating, p.fio, rh.change_date, rh.reason
        FROM rating_history rh
        JOIN profiles p ON rh.changed_by = p.id
        WHERE rh.partner_id = ?
        ORDER BY rh.change_date DESC
    ''', (partner_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def delete_partner(partner_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM profiles WHERE id = ? AND role = 'partner'", (partner_id,))
    conn.commit()
    conn.close()