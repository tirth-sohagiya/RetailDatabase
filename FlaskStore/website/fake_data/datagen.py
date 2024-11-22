from faker import Faker
from random import randint
from werkzeug.security import generate_password_hash
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import pymysql
import struct
from enum import Enum

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
    # Create database connection
    connection = pymysql.connect(
        host='aws.cjwc228ggyr7.us-west-1.rds.amazonaws.com',
        user='admin',
        password='password',
        database='SimpleStore',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    def get_product_price(product_id, connection):
        try:
            with connection.cursor() as cursor:
                sql = "SELECT price FROM product WHERE product_id = %s"
                cursor.execute(sql, (product_id,))
                result = cursor.fetchone()
                return float(result['price']) if result else 0.0
        except Exception as e:
            print(f"Error getting price for product {product_id}: {e}")
            return 0.0

    def get_user_addresses(user_id, connection):
        """Get all address IDs for a user"""
        try:
            with connection.cursor() as cursor:
                sql = "SELECT address_id FROM address WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                return [row['address_id'] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting addresses for user {user_id}: {e}")
            return []

    def get_user_payments(user_id, connection):
        """Get all payment IDs for a user"""
        try:
            with connection.cursor() as cursor:
                sql = "SELECT payment_id FROM payment WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                return [row['payment_id'] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting payments for user {user_id}: {e}")
            return []

    try:
        cursor = connection.cursor()
        for i in range(FIRSTUSER, NUM):
            user_id = i
            # Get user's addresses and payment methods
            user_addresses = get_user_addresses(user_id, connection)
            user_payments = get_user_payments(user_id, connection)
            
            # Only create orders if user has both addresses and payment methods
            if not user_addresses or not user_payments:
                continue
                
            num_orders = randint(0, 10)  # Each user has 0-10 orders
            for j in range(num_orders):
                # Get random address and payment from user's actual data
                address_id = fake.random_element(user_addresses)
                payment_id = fake.random_element(user_payments)
                order_date = fake.date_time_between(start_date='-2y', end_date='now')
                status = fake.random_element(elements=tuple(OrderStatus))  # Use proper enum values
                
                # Generate order number
                order_number = f"ORD-{fake.date_time().strftime('%Y%m')}-{str(j+1).zfill(5)}"
                
                # Create order first to get the auto-incremented ID
                order_sql = """
                    INSERT INTO customer_order (order_number, user_id, address_id, order_date, status)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(order_sql, (order_number, user_id, address_id, order_date, status.value))
                order_id = cursor.lastrowid
                
                # Generate order items
                items_per_order = randint(1, 5)  # Each order has 1-5 items
                total_amount = 0
                
                for k in range(items_per_order):
                    product_id = randint(FIRSTPRODID, LASTPRODID)
                    quantity = randint(1, 3)
                    # Get price at time of purchase
                    unit_price = get_product_price(product_id, connection)
                    total_amount += unit_price * quantity
                    
                    # Insert order item with unit_price
                    order_item_sql = """
                        INSERT INTO order_item (order_id, product_id, quantity, unit_price)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(order_item_sql, (order_id, product_id, quantity, unit_price))
                
                # Use the same or different address for billing
                billing_address_id = fake.random_element([address_id] + user_addresses)  # 50% chance same as shipping
                
                # Create transaction
                external_transaction_id = fake.uuid4()
                transaction_sql = """
                    INSERT INTO order_transaction (order_id, payment_id, billing_address_id,
                                                external_transaction_id, transaction_time, amount)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(transaction_sql, (order_id, payment_id, billing_address_id,
                                              external_transaction_id, order_date, total_amount))
                
                # Commit after each order and its related records
                connection.commit()
                
    except Exception as e:
        print(f"Error generating orders: {e}")
        connection.rollback()
    finally:
        connection.close()

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

FIRSTUSER = 2
NUM = 10000
FIRSTPRODID = 203
LASTPRODID = 223

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