use SimpleStore;

DELIMITER ;;
CREATE TRIGGER `order_date` BEFORE INSERT ON `customer_order` FOR EACH ROW
BEGIN
    SET NEW.order_date = NOW();
END;;
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER `user_date` BEFORE INSERT ON `user` FOR EACH ROW
BEGIN
    SET NEW.created_at = NOW();
END;;
DELIMITER ;;

DELIMITER ;;
CREATE TRIGGER `transaction_date` BEFORE INSERT ON `order_transaction` FOR EACH ROW
BEGIN
    SET NEW.transaction_time = NOW();
END;;
DELIMITER

DELIMITER ;;
CREATE TRIGGER `cart_date` BEFORE INSERT ON `cart` FOR EACH ROW
BEGIN
    SET NEW.added_at = NOW();
END;;
DELIMITER ;;

DELIMITER ;;
CREATE TRIGGER `rating_date` BEFORE INSERT ON `rating` FOR EACH ROW
BEGIN
    SET NEW.rating_date = NOW();
END;;
DELIMITER ;;

DELIMITER ;;
CREATE TRIGGER update_product_rating
AFTER INSERT ON rating
FOR EACH ROW
BEGIN
    UPDATE product
    SET rating = (
        SELECT AVG(rating_value)
        FROM rating
        WHERE product_id = NEW.product_id
    )
    WHERE product_id = NEW.product_id;
END;;
DELIMITER ;;



