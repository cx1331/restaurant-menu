import os
import sqlite3
import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get('DATABASE_URL')
IS_POSTGRES = DATABASE_URL is not None

def get_db():
    if IS_POSTGRES:
        # 云端使用 PostgreSQL
        return psycopg2.connect(DATABASE_URL)
    else:
        # 本地使用 SQLite
        conn = sqlite3.connect('menus.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    if IS_POSTGRES:
        create_sql = '''
            CREATE TABLE IF NOT EXISTS menus (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        '''
    else:
        create_sql = '''
            CREATE TABLE IF NOT EXISTS menus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        '''
    cursor.execute(create_sql)
    conn.commit()
    cursor.close()
    conn.close()

def load_menus():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM menus ORDER BY id')
    rows = cursor.fetchall()
    
    if IS_POSTGRES:
        menus = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    else:
        menus = [dict(row) for row in rows]
        
    cursor.close()
    conn.close()
    return menus

def add_menu_item(name, price):
    conn = get_db()
    cursor = conn.cursor()
    p = "%s" if IS_POSTGRES else "?"
    cursor.execute(f'INSERT INTO menus (name, price) VALUES ({p}, {p})', (name, price))
    conn.commit()
    cursor.close()
    conn.close()

def delete_menu_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    p = "%s" if IS_POSTGRES else "?"
    cursor.execute(f'DELETE FROM menus WHERE id = {p}', (item_id,))
    conn.commit()
    cursor.close()
    conn.close()

def search_menus_by_name(keyword):
    conn = get_db()
    cursor = conn.cursor()
    p = "%s" if IS_POSTGRES else "?"
    cursor.execute(f'SELECT * FROM menus WHERE name LIKE {p} ORDER BY id', (f'%{keyword}%',))
    rows = cursor.fetchall()
    
    if IS_POSTGRES:
        menus = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    else:
        menus = [dict(row) for row in rows]
    cursor.close()
    conn.close()
    return menus

def search_menus_by_price(min_price, max_price):
    conn = get_db()
    cursor = conn.cursor()
    p = "%s" if IS_POSTGRES else "?"
    cursor.execute(f'SELECT * FROM menus WHERE price >= {p} AND price <= {p} ORDER BY price', (min_price, max_price))
    rows = cursor.fetchall()
    
    if IS_POSTGRES:
        menus = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    else:
        menus = [dict(row) for row in rows]
    cursor.close()
    conn.close()
    return menus

# 启动时建表
init_db()
