DROP DATABASE IF EXISTS Retaildb;
CREATE DATABASE Retaildb;
USE Retaildb;

drop table if exists User;
create table User(
	uid INTEGER(11),
    email VARCHAR(40),
    name VARCHAR(40),
    phone VARCHAR(15),
    
    PRIMARY KEY(uid)
);

drop table if exists Member;
create table Member(
	uid INT(11),
    login_id VARCHAR(20),
    pass_hash CHAR(60), #Bcrypt hash will return a 60 character string as the hash (may need to adjust depending on hash alg)
    foreign key(uid) references User(uid) on delete cascade,
    primary key(uid)
);

drop table if exists Address;
 create table Address(
	address_id INT(11),
    address_line1 VARCHAR(40),
    address_line2 VARCHAR(40),
    uid INT(11),
    city VARCHAR(20),
    state VARCHAR(20),
    zip INT(5),
    country VARCHAR(20),
    primary key(address_id),
    foreign key(uid) references User(uid) on delete cascade
    );

drop table if exists Payment;
create table Payment(
	pay_id INT(11),
    card_hash CHAR(60),
    card_type ENUM('credit', 'debit', 'giftcard'),
    uid INT(11),
    primary key(pay_id),
    foreign key(uid) references User(uid) on delete cascade
    );
    
drop table if exists Guest;
create table Guest(
	uid INTEGER(11),
    card_hash CHAR(60),
    address_string VARCHAR(100),
    foreign key(uid) references User(uid) on delete cascade,
    primary key(uid)
);

drop table if exists Products;
create table Products(
	pid INT(11),
    stock INT(10),
    price INT(10),
    category VARCHAR(20),
    img_path VARCHAR(100),
    description VARCHAR(1000),
    primary key(pid)
);

drop table if exists Cart;
create table Cart(
	cid INT(11),
    uid INT(11),
    primary key(cid),
    foreign key(uid) references User(uid) on delete cascade
);

drop table if exists AddedTo;
create table AddedTo(
	pid INT(11),
    cid INT(11),
    qty INT(5),
    primary key(pid, cid),
    foreign key(pid) references Products(pid) on delete cascade,
    foreign key(cid) references Cart(cid) on delete cascade
);

drop table if exists Orders;
create table Orders(
	oid INT(11),
    date DATE,
    time TIME,
    uid INT(11),
    foreign key (uid) references User(uid),
    primary key (oid)
);

drop table if exists Contains;
create table Contains(
	oid INT(11),
    pid INT(11),
    qty INT(5),
    primary key (oid, pid),
    foreign key(pid) references Products(pid) on delete cascade,
    foreign key(oid) references Orders(oid) on delete cascade
    );

drop table if exists Transactions;
create table Transactions(
	tid INT(11),
    pay_id INT(11),
    oid INT(11),
    amount INT(12),
    foreign key(pay_id) references Payment(pay_id),
    foreign key(oid) references Orders(oid),
    primary key(tid)
    );