import sqlite3
from datetime import datetime

DB_NAME = "requests.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER NOT NULL,
            partner_name TEXT NOT NULL,
            partner_phone TEXT,
            product_artikul TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT DEFAULT 'Новая',
            request_date TEXT NOT NULL,
            prepayment_date TEXT,
            completion_date TEXT,
            comment TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_request(partner_id, partner_name, partner_phone, product_artikul, product_name, quantity, comment=""):
    conn = get_connection()
    cursor = conn.cursor()
    request_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute('''
        INSERT INTO requests (partner_id, partner_name, partner_phone, product_artikul, product_name, quantity, status, request_date, comment)
        VALUES (?, ?, ?, ?, ?, ?, 'Новая', ?, ?)
    ''', (partner_id, partner_name, partner_phone, product_artikul, product_name, quantity, request_date, comment))
    conn.commit()
    conn.close()
    return True

def get_requests_by_partner(partner_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, product_name, quantity, status, request_date, comment
        FROM requests
        WHERE partner_id = ?
        ORDER BY id DESC
    ''', (partner_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_all_requests():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, partner_name, partner_phone, product_name, quantity, status, request_date
        FROM requests
        ORDER BY id DESC
    ''')
    data = cursor.fetchall()
    conn.close()
    return data

def update_request_status(request_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    
    if status == "Выполнено":
        completion_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("UPDATE requests SET status = ?, completion_date = ? WHERE id = ?", (status, completion_date, request_id))
    else:
        cursor.execute("UPDATE requests SET status = ? WHERE id = ?", (status, request_id))
    
    conn.commit()
    conn.close()

def delete_request(request_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM requests WHERE id = ?", (request_id,))
    conn.commit()
    conn.close()