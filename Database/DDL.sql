CREATE DATABASE SimpleStore;
USE SimpleStore;

create table user(
user_id int auto_increment,
email varchar(50) unique,
pass_hash varchar(200),
created_at datetime,
first_name varchar(25),
last_name varchar(25),
primary key(user_id)
);

create table category(
category_id int auto_increment,
name varchar(25) unique,
primary key(category_id)
);

create table product(
product_id int auto_increment,
category_id int,
name varchar(50),
img_path varchar(50),
description varchar(200),
price decimal(10,2),
stock_quantity int,
rating decimal(3,2),
primary key(product_id),
foreign key(category_id) references category(category_id)
);

create table cart(
cart_id int auto_increment,
user_id int,
session_id int,
product_id int,
quantity int,
added_at datetime,
is_locked boolean,
primary key(cart_id),
foreign key(user_id) references user(user_id) on delete cascade,
foreign key(product_id) references product(product_id) on delete cascade
);

create table address(
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

create table payment(
payment_id int auto_increment,
user_id int,
payment_type enum('credit', 'debit'),
card_last_four varchar(4),
card_brand varchar(25),
expiration varchar(5), # "MM/YY"
aes_card_num varchar(300),
is_default boolean,
primary key(payment_id),
foreign key(user_id) references user(user_id) on delete cascade
);

create table rating(
rating_id int auto_increment,
user_id int,
product_id int,
stars int,
constraint stars check (stars between 1 and 5),
rating_date datetime,
primary key(rating_id),
foreign key(user_id) references user(user_id) on delete cascade,
foreign key(product_id) references product(product_id) on delete cascade
);

create table customer_order( # order is a sql keyword, cant name the table 'order'
order_id int auto_increment,
user_id int,
address_id int,
order_date datetime,
status varchar(20),
order_number varchar(20),
primary key(order_id),
foreign key(user_id) references user(user_id) on delete cascade,
foreign key(address_id) references address(address_id)
);

create table order_item(
order_item_id int auto_increment,
order_id int,
product_id int,
quantity int,
unit_price decimal,
primary key(order_item_id),
foreign key(product_id) references product(product_id),
foreign key(order_id) references customer_order(order_id) on delete cascade
);

create table order_transaction(
transaction_id int auto_increment,
order_id int,
payment_id int,
amount decimal,
payment_method enum('credit', 'debit'),
transaction_time datetime,
external_transaction_id varchar(25),
primary key(transaction_id),
foreign key(order_id) references customer_order(order_id),
foreign key(payment_id) references payment(payment_id)
);