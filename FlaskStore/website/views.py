from flask import Blueprint, render_template, request, flash, jsonify, url_for
from .queries import select_products, add_to_cart, get_cart_count, get_cart_items
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/products')
def product_route():
    result = select_products('laptop', 8)
    for prod in result:
        prod['img_path'] = url_for('static', filename=prod['img_path'])
    print(result)
    #image=url_for('static', filename='laptop.jpg' )
    return render_template("products.html", products=result)

@views.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart_route():
    data = request.get_json()
    pid = data.get('pid')
    quantity = data.get('quantity', 1)
    
    if not pid:
        return jsonify({'error': 'Product ID is required'}), 400
    
    try:
        add_to_cart(current_user.id, pid, quantity)
        cart_count = get_cart_count(current_user.id)
        return jsonify({'success': True, 'cart_count': cart_count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@views.route('/cart')
@login_required
def cart():
    cart_items = get_cart_items(current_user.id)
    return render_template("cart.html", cart_items=cart_items)