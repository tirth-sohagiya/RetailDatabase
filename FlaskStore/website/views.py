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
        prod.img_path = url_for('static', filename=prod.img_path)
    print(result)
    #image=url_for('static', filename='laptop.jpg' )
    return render_template("products.html", products=result)

@views.route('/add-to-cart', methods=['POST'])
def add_to_cart_route():
    data = request.get_json()
    pid = data.get('pid')
    quantity = data.get('quantity', 1)
    
    if not pid:
        return jsonify({'error': 'Product ID is required'}), 400
    
    try:
        # Pass uid as None for guest users
        if current_user.is_authenticated:
            uid = current_user.id  
        else: 
            uid = None
        add_to_cart(uid, pid, quantity)
        cart_count = get_cart_count(uid)
        return jsonify({'success': True, 'cart_count': cart_count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@views.route('/cart')
def cart():
    if current_user.is_authenticated:
        uid = current_user.id
    else:
        uid = None
    cart_items = get_cart_items(uid)
    return render_template("cart.html", cart_items=cart_items)