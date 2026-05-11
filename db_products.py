import sqlite3

DB_NAME = "products.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Типы продукции
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ProductType (
            product_type TEXT PRIMARY KEY,
            coefficient REAL NOT NULL
        )
    ''')
    
    # Продукция (расширенная по ТЗ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            artikul TEXT PRIMARY KEY,
            product_type TEXT NOT NULL,
            product_name TEXT NOT NULL,
            min_price REAL NOT NULL,
            roll_width REAL NOT NULL,
            description TEXT,
            length REAL,
            width REAL,
            height REAL,
            weight_no_pack REAL,
            weight_with_pack REAL,
            production_time INTEGER,
            workshop_number INTEGER,
            FOREIGN KEY (product_type) REFERENCES ProductType(product_type)
        )
    ''')
    
    # Типы материалов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MaterialType (
            material_type TEXT PRIMARY KEY,
            waste_percent REAL NOT NULL
        )
    ''')
    
    # Материалы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Materials (
            material_id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name TEXT NOT NULL,
            material_type TEXT NOT NULL,
            price REAL NOT NULL,
            stock_quantity REAL NOT NULL,
            min_quantity REAL NOT NULL,
            pack_quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            supplier TEXT,
            FOREIGN KEY (material_type) REFERENCES MaterialType(material_type)
        )
    ''')
    
    # Состав продукции
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ProductMaterials (
            artikul TEXT NOT NULL,
            material_id INTEGER NOT NULL,
            required_quantity REAL NOT NULL,
            PRIMARY KEY (artikul, material_id),
            FOREIGN KEY (artikul) REFERENCES Products(artikul) ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES Materials(material_id) ON DELETE CASCADE
        )
    ''')
    
    # Добавляем тестовые данные
    cursor.execute("SELECT COUNT(*) FROM ProductType")
    if cursor.fetchone()[0] == 0:
        # Типы продукции
        cursor.executemany("INSERT INTO ProductType VALUES (?, ?)", [
            ("Декоративные обои", 5.5),
            ("Фотообои", 7.54),
            ("Обои под покраску", 3.25),
            ("Стеклообои", 2.5)
        ])
        
        # Продукция
        cursor.executemany('''
            INSERT INTO Products (artikul, product_type, product_name, min_price, roll_width, 
            description, length, width, height, weight_no_pack, weight_with_pack, production_time, workshop_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            ("1549922", "Декоративные обои", "Обои из природного материала", 16950, 0.91, 
             "Экологичные обои из натуральных материалов", 10.5, 0.91, 0.05, 8.5, 9.2, 24, 1),
            ("2018556", "Фотообои", "Фотообои флизелиновые Горы", 15880, 0.5,
             "3D фотообои с горным пейзажем", 5.0, 2.7, 0.03, 3.2, 3.5, 12, 2),
            ("3028272", "Обои под покраску", "Обои под покраску флизелиновые Рельеф", 11080, 0.75,
             "Рельефные обои для многократной покраски", 10.0, 0.75, 0.04, 6.5, 7.0, 18, 1),
            ("4029272", "Стеклообои", "Стеклообои Рогожка белые", 5898, 1.0,
             "Стекловолокнистые обои для стен", 25.0, 1.0, 0.03, 4.5, 4.8, 8, 3),
        ])
        
        # Типы материалов
        cursor.executemany("INSERT INTO MaterialType VALUES (?, ?)", [
            ("Бумага", 0.007),
            ("Краска", 0.005),
            ("Клей", 0.0015),
            ("Дисперсия", 0.002)
        ])
        
        # Материалы
        cursor.executemany('''
            INSERT INTO Materials (material_name, material_type, price, stock_quantity, 
            min_quantity, pack_quantity, unit, supplier)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            ("Бумага-основа с покрытием", "Бумага", 1700, 2500, 1000, 100, "рул", "ООО 'Бумажные технологии'"),
            ("Концентрат печатной краски", "Краска", 1500, 550, 500, 200, "кг", "ЗАО 'Краски Плюс'"),
            ("Сухой клей на основе ПВС", "Клей", 360, 700, 500, 50, "кг", "ООО 'ХимПром'"),
            ("Флизелин", "Бумага", 1600, 2000, 1000, 140, "рул", "ООО 'Текстиль'"),
        ])
        
        # Состав продукции
        cursor.executemany("INSERT INTO ProductMaterials (artikul, material_id, required_quantity) VALUES (?, ?, ?)", [
            ("1549922", 1, 2.5),
            ("1549922", 2, 1.2),
            ("2018556", 1, 1.8),
            ("2018556", 3, 0.5),
            ("3028272", 2, 1.0),
            ("3028272", 4, 1.5),
            ("4029272", 3, 0.8),
            ("4029272", 4, 1.0),
        ])
        
        conn.commit()
        print("База данных продукции создана")
    
    conn.close()

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT artikul, product_name, product_type, roll_width, min_price, description, production_time, workshop_number FROM Products")
    data = cursor.fetchall()
    conn.close()
    return data

def get_product_by_artikul(artikul):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products WHERE artikul = ?", (artikul,))
    data = cursor.fetchone()
    conn.close()
    return data

def add_product(artikul, product_type, product_name, min_price, roll_width):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Products (artikul, product_type, product_name, min_price, roll_width)
            VALUES (?, ?, ?, ?, ?)
        ''', (artikul, product_type, product_name, min_price, roll_width))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def update_product(artikul, product_type, product_name, min_price, roll_width):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Products 
        SET product_type=?, product_name=?, min_price=?, roll_width=? 
        WHERE artikul=?
    ''', (product_type, product_name, min_price, roll_width, artikul))
    conn.commit()
    conn.close()
    return True

def delete_product(artikul):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Products WHERE artikul=?", (artikul,))
    conn.commit()
    conn.close()

def get_product_materials(artikul):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.material_name, pm.required_quantity, m.unit, m.price
        FROM ProductMaterials pm
        JOIN Materials m ON pm.material_id = m.material_id
        WHERE pm.artikul = ?
    ''', (artikul,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_material_waste_percent(material_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT mt.waste_percent 
        FROM Materials m
        JOIN MaterialType mt ON m.material_type = mt.material_type
        WHERE m.material_name = ?
    ''', (material_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def calculate_materials_for_production(artikul, quantity):
    """Рассчитать количество материалов для производства с учётом брака"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.material_name, pm.required_quantity, mt.waste_percent, m.unit, m.price
        FROM ProductMaterials pm
        JOIN Materials m ON pm.material_id = m.material_id
        JOIN MaterialType mt ON m.material_type = mt.material_type
        WHERE pm.artikul = ?
    ''', (artikul,))
    materials = cursor.fetchall()
    conn.close()
    
    result = []
    for material_name, required_qty, waste_percent, unit, price in materials:
        purchase_qty = required_qty * quantity * (1 + waste_percent)
        cost = purchase_qty * price
        result.append({
            'material': material_name,
            'required': round(required_qty * quantity, 2),
            'purchase': round(purchase_qty, 2),
            'waste_percent': round(waste_percent * 100, 2),
            'unit': unit,
            'cost': round(cost, 2)
        })
    return result

def calculate_product_cost(artikul):
    """Рассчитать себестоимость продукции с учётом брака материалов"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT min_price, product_type FROM Products WHERE artikul = ?", (artikul,))
    product = cursor.fetchone()
    if not product:
        conn.close()
        return 0
    min_price, product_type = product
    
    cursor.execute("SELECT coefficient FROM ProductType WHERE product_type = ?", (product_type,))
    coeff = cursor.fetchone()
    coefficient = coeff[0] if coeff else 1
    
    cursor.execute('''
        SELECT pm.required_quantity, m.price, mt.waste_percent
        FROM ProductMaterials pm
        JOIN Materials m ON pm.material_id = m.material_id
        JOIN MaterialType mt ON m.material_type = mt.material_type
        WHERE pm.artikul = ?
    ''', (artikul,))
    materials = cursor.fetchall()
    conn.close()
    
    cost_price = sum(q * p * (1 + waste) for q, p, waste in materials)
    final_cost = cost_price * coefficient
    
    if final_cost < min_price:
        final_cost = min_price
    
    return round(final_cost, 2)