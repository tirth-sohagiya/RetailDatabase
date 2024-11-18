# This file will be used to store all common queries that our site will need to make to the db
# as to not clutter other files and have them deal with connections and such
from . import connection as conn
import logging
import pymysql

def get_password(email): 
    sql = "SELECT pass_hash from user WHERE email = %s"
    conn.ping()
    with conn.cursor() as cursor:         
        cursor.execute(sql, (email))
        results = cursor.fetchall()
    return results[0]['pass_hash']

def create_user(email, name, pass_hash):
    sql = "INSERT INTO user (email, name, pass_hash) VALUES (%s, %s, %s)"
    # pinging connection with db, was getting some errors without this
    conn.ping()
    with conn.cursor() as cursor:         
        cursor.execute(sql, (email, name, pass_hash))
        conn.commit()

def select_products(category, num):
    sql = "SELECT pid, name, price, description, img_path FROM product WHERE category = %s ORDER BY popularity DESC LIMIT %s"
    with conn.cursor() as cursor:         
        cursor.execute(sql, (category, num))
        results = cursor.fetchall()
    return results

def add_to_cart(uid, pid, quantity=1):
    sql = """
        INSERT INTO cart (uid, p_id, quantity) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE quantity = quantity + %s
    """
    conn.ping()
    with conn.cursor() as cursor:
        cursor.execute(sql, (user_id, product_id, quantity, quantity))
        conn.commit()

def get_cart_count(user_id):
    sql = "SELECT SUM(quantity) as count FROM cart WHERE uid = %s"
    conn.ping()
    with conn.cursor() as cursor:
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result['count'] if result['count'] else 0

def get_cart_items(user_id):
    sql = """
        SELECT p.name, p.price, p.img_path, c.quantity, p.pid
        FROM cart c
        JOIN product p ON c.pid = p.pid
        WHERE c.id = %s
    """
    conn.ping()
    with conn.cursor() as cursor:
        cursor.execute(sql, (user_id,))
        return cursor.fetchall()
