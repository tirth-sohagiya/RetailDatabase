from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect
from .queries import select_products, add_to_cart, get_cart_count, get_cart_items, delete_from_cart,\
set_all_product_ratings, get_addresses, get_payments, create_order_transaction, search_products
from flask_login import login_required, current_user
from .models import Address, Payment
from . import db

views = Blueprint('views', __name__)

# products is now the home page
@views.route('/', methods=['GET', 'POST'])
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
    search_term = request.args.get('q', '').strip()
    sort_by = request.args.get('sort_by', 'default')
    sort_order = request.args.get('sort_order', 'asc')
    products = []

    if search_term:
        try:
            results = search_products(search_term, sort_by, sort_order)
            print(f"Search results: {results}")  # Debug log for results
            for result in results:
                product = result[0]
                product.category_id = result[1]
                product.category_name = result[2]
                products.append(product)
        except Exception as e:
            print(f"Error in search: {str(e)}")

    return render_template("products.html", products=products, search_term=search_term)

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
        print("Cart count:", cart_count)
        return jsonify({
            'success': True,
            'message': 'Item added to cart', 
            'cart_count': cart_count
        }), 200
    except Exception as e:
        print("Error adding to cart:", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
        return jsonify({
            'success': True,
            'message': 'Item removed from cart'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# upon deciding to checkout, we need to lock the user's cart so that they can't add more items in another tab or session
# then serve them the checkout page that allows them to select payment method/addresses
# need an unlocking procedure if they bail on the checkout
# finalize checkout occurs after user has selected payment method/addresses
# we will create the order and transaction records from the cart
@views.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'GET':
        return render_template("checkout.html", cart_items=get_cart_items(current_user.id), 
        addresses=get_addresses(current_user.id), payment_methods=get_payments(current_user.id))

    if request.method == 'POST':
        # Get form data
        for entry in request.form:
            print(entry, request.form.get(entry))
        payment_id = request.form.get('payment_id')
        billing_address_id = request.form.get('billing_address_id')
        shipping_address_id = request.form.get('shipping_address_id')
        print("shipping_address_id:", shipping_address_id)

        # If the user submitted a new address during checkout, add it to the database
        if shipping_address_id == 'new':
            new_address = Address(user_id=current_user.id, street_address=request.form.get('street'), city=request.form.get('city'), state=request.form.get('state'), zip=request.form.get('zip_code'))
            db.session.add(new_address)
            db.session.commit()
            shipping_address_id = new_address.address_id

        # If the user submitted a new payment method during checkout, add it to the database
        if payment_id == 'new':
            new_payment = Payment(user_id=current_user.id, card_number=request.form.get('card_number'), exp_date=request.form.get('exp_date'), cvv=request.form.get('cvv'))
            db.session.add(new_payment)
            db.session.commit()
            payment_id = new_payment.payment_id

        # If we received no billing address ID, we assume it's the same as shipping
        # if the billing address is a new address, we need to add it to the database
        if billing_address_id ==None:
            billing_address_id = shipping_address_id
        elif billing_address_id == 'new':
            # add billing address to the database
            new_address = Address(user_id=current_user.id, street_address=request.form.get('billing_street'), city=request.form.get('billing_city'), state=request.form.get('billing_state'), zip=request.form.get('billing_zip'))
            db.session.add(new_address)
            db.session.commit()
            billing_address_id = new_address.address_id

        # print("Payment ID:", payment_id)
        # print("Billing Address ID:", billing_address_id)
        # print("Shipping Address ID:", shipping_address_id)
        create_order_transaction(current_user.id, payment_id, billing_address_id, shipping_address_id)
        flash('Order has been placed successfully!', category='success')
        return redirect(url_for('views.store_home'))

@views.context_processor
def cart_count_processor():
    """Add cart count to all templates"""
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = None
    return dict(cart_count=get_cart_count(user_id))
