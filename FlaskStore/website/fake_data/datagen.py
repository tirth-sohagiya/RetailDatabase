from faker import Faker
from random import randint
from werkzeug.security import generate_password_hash
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
FIRSTUSER = 2
NUM = 10000
FIRSTPRODID = 203
LASTPRODID = 223
import struct

def bytes_to_bits_binary(byte_data):
    bits_data = bin(int.from_bytes(byte_data, byteorder='big'))[2:]
    return bits_data


fake = Faker()

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
    with open('orders.txt', 'w+') as f1, open('order_items.txt'):
        for i in range(FIRSTUSER, NUM):
            num_orders = randint(0, 10)
            for j in range(num_orders):
                items_per_order = randint(1, 10):


def fake_carts():
    pass

def fake_transactions():
    pass
                

        

    

if __name__ == "__main__":
    #gen_payment()
    #gen_user()
    #gen_address()
    fake_rating()

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
);"""