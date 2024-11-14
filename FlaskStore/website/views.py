from flask import Blueprint, render_template, url_for
from .queries import select_products

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/products')
def products():
    result = select_products('laptop', 1)
    print(result)
    #image=url_for('static', filename='laptop.jpg' )
    prod = format_sql(result, 1)
    return render_template("products.html", **prod)

def format_sql(result, num_products):
    prod = {}
    for i in range(num_products):
        idx = str(i)
        prod['pname' + idx] = result[i]['pname']
        prod['price' + idx] = result[i]['price']
        prod['description' + idx] = result[i]['description']
        prod['img_path' + idx] = url_for('static', filename=result[i]['img_path'])
    print(prod['img_path0'])
    return prod
@views.route('/cart')
def cart():
    return render_template("cart.html")