import os
import sqlite3
import psycopg2
import psycopg2.extras

# 核心：在这里定义变量，电脑就不会报错了
DATABASE_URL = os.environ.get('DATABASE_URL')
IS_POSTGRES = DATABASE_URL is not None

def get_db():
    if IS_POSTGRES:
        print("正在使用：云端 PostgreSQL 数据库")
        return psycopg2.connect(DATABASE_URL)
    else:
        print("正在使用：本地 SQLite 数据库")
        # 获取当前文件所在的绝对路径，强制数据库跟代码在同一目录
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, 'restaurant.db')

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 针对不同数据库的自增主键写法
    if IS_POSTGRES:
        create_menus_sql = '''
            CREATE TABLE IF NOT EXISTS menus (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL
            )
        '''
        # 建用户表 (PostgreSQL版)
        create_uers_sql = '''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        '''
    else:
        create_menus_sql = '''
            CREATE TABLE IF NOT EXISTS menus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL
                )
            '''
        # 建用户表 (SQLite版)
        create_uers_sql = '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
                )
            '''

    cursor.execute(create_menus_sql)
    cursor.execute(create_uers_sql)
    conn.commit()
    cursor.close()
    conn.close()

def load_menus():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM menus ORDER BY id')
    rows = cursor.fetchall()

    columns = [column[0] for column in cursor.description]
    menus = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    conn.close()
    return menus

def add_menu(name, quantity, price):
    conn = get_db()
    cursor = conn.cursor()

    m = "%s" if IS_POSTGRES else "?"
    sql = f'INSERT INTO menus (name, quantity, price) VALUES ({m}, {m}, {m})'

    cursor.execute(sql, (name, quantity, price))
    conn.commit()
    cursor.close()
    conn.close()

def delete_menu(menu_id):
    conn = get_db()
    cursor = conn.cursor()
    m = "%s" if IS_POSTGRES else "?"
    cursor.execute(f'DELETE FROM menus WHERE id = {m}', (menu_id,))
    conn.commit()
    cursor.close()
    conn.close()

def update_stock(menu_id, new_quantity):
    conn = get_db()
    cursor = conn.cursor()
    m = "%s" if IS_POSTGRES else "?"
    cursor.execute(f'UPDATE menus SET quantity = {m} WHERE id = {m}', (new_quantity, menu_id))
    conn.commit()
    cursor.close()
    conn.close()

def search_menus_by_name(keyword):
    conn = get_db()
    cursor = conn.cursor()
    m = "%s" if IS_POSTGRES else "?"
    cursor.execute(f'SELECT * FROM menus WHERE name LIKE {m} ORDER BY id', (f'%{keyword}%',))
    rows = cursor.fetchall()

    if IS_POSTGRES:
        menus = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    else:
        menus = [dict(row) for row in rows]
    cursor.close()
    conn.close()
    return menus

# 根据用户名查找用户 （登录时用）
def get_user_by_username(username):
    conn = get_db()
    cursor = conn.cursor()
    m = "%s" if IS_POSTGRES else "?"
    cursor.execute(f'SELECT * FROM users WHERE username = {m}', (username,))
    row = cursor.fetchone()

    if row:
        columns = [column[0] for column in cursor.description]
        user = dict(zip(columns, row))
    else:
        user = None

    cursor.close()
    conn.close()
    return user

# 创建新用户（初始化管理员密码时用）
def create_user(username, password_hash):
    conn = get_db()
    cursor = conn.cursor()
    m = "%s" if IS_POSTGRES else "?"
    try:
        cursor.execute(f'INSERT INTO users (username, password_hash) VALUES ({m}, {m})', (username, password_hash))
        conn.commit()
        return True
    except Exception as e:
        # 如果用户名已存在，会报错，直接返回 False
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# 启动时建表
init_db()
