from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', "POST"])
def login():
    data = request.form
    print(data)
    return render_template("login.html", text="Testing")

@auth.route('/logout')
def logout():
    return "<p>Logout</p>"

@auth.route('/create_account', methods=['GET', "POST"])
def create_account():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Email must be at least 4 characters', category='error')
        elif len(name) < 2:
            flash('Name must be at least 2 characters', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')
        elif len(password2) < 7:
            flash('Password must be at least 7 characters', category='error')
        else:
            #add user to database
            flash('Account created!', category='success')
    return render_template("create_account.html")