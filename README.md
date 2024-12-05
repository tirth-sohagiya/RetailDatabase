# Flask E-commerce Store

## How to Use

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`
4. Access the store at: `http://localhost:5000`

## Project Structure

### Core Files

- `__init__.py`: Application factory that initializes Flask app, database, and login manager. Sets up blueprints and configurations.

- `models.py`: Defines SQLAlchemy database models including:
  - User: Customer account information
  - Product: Store inventory items
  - Cart: Shopping cart implementation with locking mechanism
  - Order/OrderItem: Order processing
  - Transaction: Payment processing
  - Address/Payment: Customer shipping and payment information

- `queries.py`: Contains all database operations and business logic:
  - Cart management (add, remove, clear)
  - Product operations (search, filter, sort)
  - Transaction processing
  - Cart locking mechanism for concurrent access
  - Address and payment method management

- `views.py`: Main route handlers for store functionality:
  - Store homepage and product browsing
  - Shopping cart operations
  - Checkout process
  - Product search and filtering

- `auth.py`: Authentication-related routes and logic:
  - User registration
  - Login/logout
  - Account settings
  - Address/payment management
  - Order history

### Data Generation

The `website/fake_data/` directory contains scripts and data used to populate the database with test data:
- Product information
- User accounts
- Test passwords
- Sample transactions

## Key Features

1. **Secure Shopping Cart**
   - Cart locking mechanism prevents concurrent modifications during checkout
   - Session-based cart for guest users
   - Cart transfer upon user login

2. **Transaction Processing**
   - Atomic database operations
   - Inventory management
   - Order tracking

3. **User Management**
   - Secure password hashing
   - Address book
   - Payment method storage
   - Order history

4. **Product Management**
   - Search functionality
   - Category filtering
   - Sort options
   - Stock tracking

## Security Features

- Password hashing using Werkzeug
- Session management
- Cart locking mechanism
- Secure payment info storage

## Database Design

The application uses SQLAlchemy ORM with the following key relationships:
- User -> Orders (one-to-many)
- Order -> OrderItems (one-to-many)
- Order -> Transaction (one-to-one)
- User -> Addresses (one-to-many)
- User -> Payments (one-to-many)