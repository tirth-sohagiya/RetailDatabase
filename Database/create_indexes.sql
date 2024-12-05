use SimpleStore;

# product
create index prod_cat on product(product_id, category_id);
create index prod_price on product (price);
create index prod_rating on product (rating);

# user
create index uid on user(user_id);
create index email on user(email);

# rating
create index user_id on rating(user_id);
create index product_id on rating(product_id);

# payment
create index payment_id on rating(payment_id);

# order_transaction
create index order_id on order_transaction(order_id);
create index payment_id on order_transaction(payment_id);
create index billing_address_id on order_transaction(billing_address_id);

# order_item
create index order_id on order_item(order_id);
create index proudct_id on order_item(product_id);

# customer_order
create index user_id on customer_order(user_id);
create index address_id on customer_order(address_id);

# category
create index name on category(category_name);
create index cat_idx on category(category_id);

# cart
create index user_id on cart(user_id);
create index product_id on cart(product_id);

# address
create index user_id on address(user_id);


