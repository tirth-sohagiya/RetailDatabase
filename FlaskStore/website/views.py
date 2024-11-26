from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect
from .queries import select_products, add_to_cart, get_cart_count, get_cart_items, delete_from_cart, set_all_product_ratings, update_product_image_paths
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

# products is now the home page
@views.route('/', methods=['GET', "POST"])
def store_home():
    try:
        # Get sorting parameters from request
        sort_by = request.args.get('sort_by', 'default')
        sort_order = request.args.get('sort_order', 'asc')
        
        results = select_products('laptop', 20, sort_by, sort_order)
        products = []
        for result in results:
            product = result[0]  # Get the Product object
            product.category_id = result[1]  # Add category_id
            product.category_name = result[2]  # Add category_name
            products.append(product)

    except Exception as e:
        print(f"Error in store_home: {str(e)}")  # Add logging
        # If there's an error, clear the cache and try again
        select_products.cache_clear()
        return redirect(url_for('views.store_home'))
        
    return render_template("products.html", products=products,
                         current_sort=sort_by, 
                         current_order=sort_order)

@views.route('/search', methods=['GET', "POST"])
def search():
    pass

@views.route('/cart')
def cart():
    """Display cart page"""
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = None
    return render_template("cart.html", cart_items=get_cart_items(user_id))

@views.route('/add-to-cart', methods=['POST'])
def add_to_cart_route():
    """Add item to cart"""
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    try:
        # Pass user_id as None for guest users
        if current_user.is_authenticated:
            user_id = current_user.id  
        else:
            user_id = None
        add_to_cart(user_id, product_id, quantity)
        cart_count = get_cart_count(user_id)
        return jsonify({'message': 'Item added to cart', 'cart_count': cart_count}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@views.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    """Delete item from cart"""
    data = request.get_json()
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    try:
        if current_user.is_authenticated:
            delete_from_cart(product_id, current_user.id)
        else:
            delete_from_cart(product_id)
        return jsonify({'message': 'Item deleted from cart'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@views.context_processor
def cart_count_processor():
    """Add cart count to all templates"""
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = None
    return dict(cart_count=get_cart_count(user_id))

def set_product_objects(results: list) -> list:
    
    return products