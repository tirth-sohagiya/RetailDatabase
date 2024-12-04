use SimpleStore;

create view user_addresses as
select u.user_id, u.first_name, u.last_name, u.email, a.address_id, a.street_address,
a.city, a.state, a.zip, a.country, a.is_default
from user u, address a
where u.user_id = a.user_id;

create view user_payments as
select u.user_id, u.first_name, u.last_name, u.email, p.payment_id, p.payment_type,
p.card_last_four, p.card_brand, p.expiration, p.is_default
from user u, payment p
where u.user_id = p.user_id;

create view transaction_view as 
select u.user_id, u.email, o.order_id, o.order_date, o.order_number, o.status, o.address_id as shipping_address_id,
t.transaction_id, t.payment_id, t.amount, t.billing_address_id
from user u, customer_order o, order_transaction t
where u.user_id = o.user_id and o.order_id = t.order_id;