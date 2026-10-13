import sqlite3
import os

DATABASE = 'menus.db'

# ----- 数据库连接 （自动提交、回滚、关闭） -----
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ----- 初始化表 -----
def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS menus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ----- 加载所有菜单 -----
def load_menus():
    conn = get_db()
    rows = conn.execute('SELECT * FROM menus ORDER BY id').fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ----- 添加菜品 -----
def add_menu_item(name, price):
    conn = get_db()
    conn.execute('INSERT INTO menus (name, price) VALUES (?, ?)', (name, price))
    conn.commit()
    conn.close()

# ----- 删除菜品 (按 ID) -----
def delete_menu_item(item_id):
    conn = get_db()
    conn.execute('DELETE FROM menus WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

# ----- 搜索菜名 (模糊匹配) -----
def search_menus_by_name(keyword):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM menus WHERE name LIKE ? ORDER BY id',
        (f'%{keyword}%',)        
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ----- 按价格区间搜索 -----
def search_menus_by_price(min_price, max_price):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM menus WHERE price >= ? AND price <= ? ORDER BY price',
        (min_price, max_price)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ----- 程序启动时建表 -----
init_db()