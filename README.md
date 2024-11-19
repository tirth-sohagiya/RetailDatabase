
# Flask Retail Store Application

This is a Flask-based web application for a retail store with user authentication and shopping cart functionality.

## Project Structure

The application is organized into several Python modules, each with specific responsibilities:

### 1. [__init__.py](https://github.com/lucas-peters/RetailDatabase/blob/main/FlaskStore/website/__init__.py)
Main application configuration and initialization:
- [create_app()](https://github.com/lucas-peters/RetailDatabase/blob/main/FlaskStore/website/__init__.py#L16): Creates and configures the Flask application
  - Initializes SQLAlchemy database connection
  - Sets up Flask-Login for user authentication
  - Registers blueprints for views and authentication

### 2. [models.py](https://github.com/lucas-peters/RetailDatabase/blob/main/FlaskStore/website/models.py)
Database models using SQLAlchemy:
- `User`: User model for authentication
  - `get_id()`: Returns user ID for Flask-Login
  - `id`: Property for Flask-Login compatibility
- `Product`: Product model for store items
  - `get_id()`: Returns product ID
- `Cart`: Shopping cart model
  - Stores user's selected items

### 3. [views.py](https://github.com/lucas-peters/RetailDatabase/blob/main/FlaskStore/website/views.py)
Main application routes and views:
- [home()](https://github.com/lucas-peters/RetailDatabase/blob/main/FlaskStore/website/views.py#L8): Renders the homepage
- [product_route()](https://github.com/lucas-peters/RetailDatabase/blob/main/FlaskStore/website/views.py#L12): Displays product listings
- [add_to_cart_route()](https://github.com/lucas-peters/RetailDatabase/blob/main/FlaskStore/website/views.py#L21): Handles adding items to cart
  - Accepts POST requests with product ID and quantity
  - Supports both authenticated and guest users
- [cart()](https://github.com/lucas-peters/RetailDatabase/blob/main/FlaskStore/website/views.py#L41): Displays the user's shopping cart

### 4. [auth.py](https://github.com/lucas-peters/RetailDatabase/blob/main/FlaskStore/website/auth.py)
Authentication-related routes and functions:
- [login()](https://github.com/lucas-peters/RetailDatabase/blob/main/FlaskStore/website/auth.py#L11): Handles user login
  - Validates credentials
  - Creates user session
- [logout()](https://github.com/lucas-peters/RetailDatabase/blob/main/FlaskStore/website/auth.py#L24): Handles user logout
- [create_account()](https://github.com/lucas-peters/RetailDatabase/blob/main/FlaskStore/website/auth.py#L28): New user registration
  - Validates user input
  - Creates new user accounts
  - Implements password hashing

### 5. [test.py](https://github.com/lucas-peters/RetailDatabase/blob/main/FlaskStore/test.py)
Database testing and setup:
- Contains database connection testing
- Creates initial database schema
- Includes test data insertion

## Database Configuration

The application uses MySQL with AWS RDS:
- Host: aws.cjwc228ggyr7.us-west-1.rds.amazonaws.com
- Database: flasktest
- Connection managed through SQLAlchemy ORM

## Security Features

- Password hashing using Werkzeug security
- Flask-Login for session management
- CSRF protection through Flask-WTF
- Secure password validation rules

## Routes

- `/`: Homepage
- `/login`: User login
- `/logout`: User logout
- `/create_account`: New user registration
- `/products`: Product listing
- `/cart`: Shopping cart
- `/add-to-cart`: Cart manipulation (POST)

## Dependencies

- Flask
- Flask-SQLAlchemy
- Flask-Login
- PyMySQL
- Werkzeug
