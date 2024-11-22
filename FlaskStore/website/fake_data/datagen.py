from faker import Faker
from random import randint
from werkzeug.security import generate_password_hash
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import pymysql
import struct
from enum import Enum

# Constants for data generation
FIRSTUSER = 2
NUM = 10000
FIRSTPRODID = 203
LASTPRODID = 223

# Import OrderStatus from models to ensure consistency
class OrderStatus(str, Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

fake = Faker()

def bytes_to_bits_binary(byte_data):
    bits_data = bin(int.from_bytes(byte_data, byteorder='big'))[2:]
    return bits_data


def gen_user():
    with open('fake_users.txt', 'w+') as f, open('passwords.txt', 'w+') as p:
        for i in range(FIRSTUSER, NUM):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name}.{last_name}@{fake.domain_name()}"
            password = fake.password()
            pass_hash = generate_password_hash(password)
            created_at = fake.date_time()
            user_string = f"('{email}', '{first_name}', '{last_name}', '{pass_hash}', '{created_at}'),"
            print(user_string, file=f)
            if i < 10:
                print("email:", email, "password:", password, file=p)

def gen_payment():
    key = get_random_bytes(32)
    with open('key.txt', 'w+') as k:
        print(key, file=k)
    cipher = AES.new(key, AES.MODE_GCM)
    credit = randint(0,1)
    with open('payment.txt', 'w+') as f:
        for i in range(FIRSTUSER, NUM):
            num = randint(1, 3) # users will randomly have between 1 and 3 payments
            for j in range(num):
                credit = randint(0,1)
                user_id = i
                payment_type = 'credit' if credit else 'debit'
                card_number = fake.credit_card_number()
                # encrypting full credit card number
                encryption = str(cipher.encrypt(card_number.encode()))
                # turning bytes string into binary, so that it can be stored in sql
                aes_card_num = ''.join(format(ord(i), '08b') for i in encryption)
                card_last_four = card_number [-4:] # this gets the last 4 characters of the credit card string
                expiration = fake.credit_card_expire()
                card_brand = fake.credit_card_provider()
                if j == 0:
                    is_default = 1
                else:
                    is_default = 0
                payment_string = f"({user_id}, '{payment_type}', '{aes_card_num}', '{card_last_four}', '{expiration}', {is_default}, '{card_brand}'),"
                print(payment_string, file=f)
            

def gen_address():
    with open('address.txt', 'w+') as f:
        for i in range(FIRSTUSER, NUM):
            num = randint(0,3) # users will randomly have between 0 and 3 addresses
            user_id = i
            for j in range(num):
                street_address = fake.street_address()
                city = fake.city()
                state = fake.state()
                zipcode = fake.zipcode()
                country = 'United States'
                is_default = 1 if j == 0 else 0
                address_string = f"({user_id}, '{street_address}', '{city}', '{state}', '{zipcode}', '{country}', {is_default}),"
                print(address_string, file=f)

def fake_rating():
    with open ('ratings.txt', 'w+') as f:
        for i in range(FIRSTUSER, NUM):
            num_ratings = randint(1, 10) # each user will leave between 1 and 10 ratings
            for j in range(num_ratings):
                user_id = i
                product_id = randint(FIRSTPRODID, LASTPRODID) # randomly choosing a product that the user rated
                rand = randint(1, 100) # using this for a weighted prob, users are more likely to leave 5 stars
                if rand > 50:
                    stars = 5
                elif rand > 25:
                    stars = 4
                elif rand > 17:
                    stars = 3
                elif rand > 8:
                    stars = 2
                else:
                    stars = 1
                rating_date = fake.date_time()
                rating_string = f"({user_id}, {product_id}, {stars}, '{rating_date}'),"
                print(rating_string, file=f)
            
def fake_orders():
    print(f"Starting order generation for users {FIRSTUSER} to {NUM}")
    # Create output file for SQL statements
    with open('order_inserts.sql', 'w') as f:
        # Get all user data
        connection = pymysql.connect(
            host='aws.cjwc228ggyr7.us-west-1.rds.amazonaws.com',
            user='admin',
            password='password',
            database='SimpleStore',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        try:
            cursor = connection.cursor()
            
            # Get addresses
            cursor.execute("SELECT user_id, address_id FROM address")
            addresses = cursor.fetchall()
            print(f"Found {len(addresses)} addresses")
            
            # Get payments
            cursor.execute("SELECT user_id, payment_id FROM payment")
            payments = cursor.fetchall()
            print(f"Found {len(payments)} payments")
            
            # Get product prices
            cursor.execute("SELECT product_id, price FROM product")
            product_prices = {row['product_id']: float(row['price']) for row in cursor.fetchall()}
            print(f"Found {len(product_prices)} products")
            
            # Organize data by user
            user_data = {}
            for row in addresses:
                user_id = row['user_id']
                if user_id not in user_data:
                    user_data[user_id] = {'addresses': [], 'payments': []}
                user_data[user_id]['addresses'].append(row['address_id'])
                
            for row in payments:
                user_id = row['user_id']
                if user_id not in user_data:
                    user_data[user_id] = {'addresses': [], 'payments': []}
                user_data[user_id]['payments'].append(row['payment_id'])
            
            print(f"Found data for {len(user_data)} users")
            
        finally:
            connection.close()

        # Initialize lists to store values
        order_values = []
        order_item_values = []
        transaction_values = []
        
        order_id = 1  # Start with order_id 1
        users_with_orders = 0
        
        for i in range(FIRSTUSER, NUM):
            print("i")
            if i not in user_data or not user_data[i]['addresses'] or not user_data[i]['payments']:
                continue
            print("still in loop")    
            user_addresses = user_data[i]['addresses']
            user_payments = user_data[i]['payments']
            
            num_orders = randint(0, 5)  # Reduced max orders per user
            if num_orders > 0:
                users_with_orders += 1
                
            for j in range(num_orders):
                address_id = fake.random_element(user_addresses)
                payment_id = fake.random_element(user_payments)
                order_date = fake.date_time_between(start_date='-2y', end_date='now')
                status = fake.random_element(elements=tuple(OrderStatus))
                order_number = f"ORD-{fake.date_time().strftime('%Y%m')}-{str(j+1).zfill(5)}"
                
                # Add order values
                order_values.append(
                    f"({order_id}, '{order_number}', {i}, {address_id}, '{order_date}', '{status.value}')"
                )
                
                # Generate order items
                items_per_order = randint(1, 3)
                total_amount = 0
                
                for k in range(items_per_order):
                    product_id = randint(FIRSTPRODID, LASTPRODID)
                    quantity = randint(1, 3)
                    unit_price = product_prices.get(product_id, 0.0)
                    total_amount += unit_price * quantity
                    
                    # Add order item values
                    order_item_values.append(
                        f"({order_id}, {product_id}, {quantity}, {unit_price})"
                    )
                
                # Add transaction values
                billing_address_id = fake.random_element(user_addresses)
                external_transaction_id = fake.uuid4()
                transaction_values.append(
                    f"({order_id}, {payment_id}, {billing_address_id}, '{external_transaction_id}', '{order_date}', {total_amount})"
                )
                
                order_id += 1

        print(f"Generated orders for {users_with_orders} users")
        print(f"Total orders: {len(order_values)}")
        print(f"Total order items: {len(order_item_values)}")
        print(f"Total transactions: {len(transaction_values)}")

        # Write all inserts to file
        f.write("INSERT INTO customer_order (order_id, order_number, user_id, address_id, order_date, status) VALUES\n")
        f.write(",\n".join(order_values))
        f.write(";\n\n")

        f.write("INSERT INTO order_item (order_id, product_id, quantity, unit_price) VALUES\n")
        f.write(",\n".join(order_item_values))
        f.write(";\n\n")

        f.write("INSERT INTO order_transaction (order_id, payment_id, billing_address_id, external_transaction_id, transaction_time, amount) VALUES\n")
        f.write(",\n".join(transaction_values))
        f.write(";\n")

def fake_transactions():
    # This function is no longer needed as transactions are created in fake_orders
    pass

def fake_carts():
    with open('carts.txt', 'w+') as f:
        for i in range(FIRSTUSER, NUM):
            cart_chance = randint(1,10)  # 10% chance a user has an active cart
            if cart_chance == 1:
                num_items = randint(1, 10)
                for j in range(num_items):
                    user_id = i
                    product_id = randint(FIRSTPRODID, LASTPRODID)
                    quantity = randint(1, 5)
                    added_at = fake.date_time()
                    session_id = fake.uuid4()  # Add session_id for guest carts
                    cart_string = f"({user_id}, {product_id}, '{session_id}', {quantity}, '{added_at}'),"
                    print(cart_string, file=f)

if __name__ == "__main__":
    #gen_payment()
    #gen_user()
    #gen_address()
    #fake_rating()
    #fake_carts()
    fake_orders()

"""payment_id int auto_increment,
user_id int,
payment_type enum('credit', 'debit'),
card_last_four varchar(4),
card_brand varchar(25),
expiration varchar(5), # "MM/YY"
is_default boolean,
primary key(payment_id),
foreign key(user_id) references user(user_id) on delete cascade

address_id int auto_increment,
user_id int,
street_address varchar(100),
city varchar(50),
state varchar(50),
zip varchar(10),
country varchar(50),
is_default boolean,
primary key(address_id),
foreign key(user_id) references user(user_id) on delete cascade
);
"""