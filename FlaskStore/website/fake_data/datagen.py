from faker import Faker
from random import randint
from werkzeug.security import generate_password_hash
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
NUM = 10000
import struct

def bytes_to_bits_binary(byte_data):
    bits_data = bin(int.from_bytes(byte_data, byteorder='big'))[2:]
    return bits_data


fake = Faker()

def gen_user():
    with open('fake_users.txt', 'w+') as f, open('passwords.txt', 'w+') as p:
        for i in range(1, NUM):
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
        for i in range(2, NUM):
            num = randint(1, 3)
            for j in range(num):
                credit = randint(0,1)
                user_id = i
                payment_type = 'credit' if credit else 'debit'
                card_number = fake.credit_card_number()
                aes_card_num = cipher.encrypt(card_number.encode())
                card_last_four = card_number [-4:]
                expiration = fake.credit_card_expire()
                card_brand = fake.credit_card_provider()
                if j == 0:
                    is_default = 1
                else:
                    is_default = 0
                payment_string = f"({user_id}, '{payment_type}', '{bytes_to_bits_binary(aes_card_num.bin)}', '{card_last_four}', '{expiration}', {is_default}, '{card_brand}'),"
                print(payment_string, file=f)
            

def gen_address():
    with open('address.txt', 'w+') as f:
        for i in range(1, NUM):
            num = randint(0,3)
            user_id = i
            for j in range(num):
                street_address = fake.street_address()
                city = fake.city()
                state = fake.state()
                zipcode = fake.zipcode()
                country = 'United States'
                is_default = 1 if j is 0 else 0
                address_string = f"({user_id}, '{street_address}', '{city}', '{state}', '{zipcode}', '{country}', {is_default}),"
                print(address_string, file=f)
                

        

    

if __name__ == "__main__":
    gen_payment()
    #gen_user()
    #gen_address()

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