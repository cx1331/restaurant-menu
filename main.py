from flask import Flask, redirect, url_for, request, render_template
from res_db import(
    load_menus, add_menu_item, delete_menu_item, search_menus_by_name, search_menus_by_price
)

app = Flask(__name__)



# ----- 首页 -----
@app.route('/')
def home():
    return "<a href='/menus'> 进入菜单管理</a>"

# ----- 显示菜单 （含搜索框）-----
@app.route('/menus')
def show_menus():
    menus = load_menus()
    return render_template('menu.html', menus=menus)


# ----- 添加菜品 (表单页面) -----
@app.route('/add_form')
def add_form():
    return render_template('add_form.html')

# ----- 执行添加 -----
@app.route('/add')
def add():
    name = request.args.get('name', '').strip()
    price_str = request.args.get('price', '').strip()

    if not name or not price_str:
        return "名称和价格不能为空", 400

    try:
        price = float(price_str)
    except ValueError:
        return "价格必须是数字", 400

    add_menu_item(name, price)
    return redirect(url_for('show_menus'))

# ----- 删除菜品 -----
@app.route('/delete/<int:item_id>')
def delete(item_id):
    delete_menu_item(item_id)
    return redirect(url_for('show_menus'))

# ----- 按菜名搜索 -----
@app.route('/search')
def search_menu():
    keyword = request.args.get('q', '').strip()
    if not keyword:
        return redirect(url_for('show_menus'))
    results = search_menus_by_name(keyword)
    return render_template('search_result.html', title=f"搜索 '{keyword}' 的结果", results=results)

# ----- 按价格区间搜索 -----
@app.route('/search_price')
def search_price():
    min_str = request.args.get('min', '').strip()
    max_str = request.args.get('max', '').strip()

    # 缺省值: 0 到 9999
    try:
        min_p = float(min_str) if min_str else 0
        max_p = float(max_str) if max_str else 9999
    except ValueError:
        return "请输入有效的数字", 400

    if min_p > max_p:
        return "最低价不能高于最高价", 400

    results = search_menus_by_price(min_p, max_p)

    return render_template('search_result.html', title=f"价格 {min_p:.2f} ~ {max_p:.2f} 的菜品", results=results)


# ----- 启动服务器 -----
if __name__ == '__main__':
    app.run(debug=True)