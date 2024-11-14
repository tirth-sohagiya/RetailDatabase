# This file will be used to store all common queries that our site will need to make to the db
# as to not clutter other files and have them deal with connections and such
from . import connection as conn
import logging
import pymysql

def get_password(email): 
    sql = """SELECT pass_hash from user WHERE email = %s"""
    conn.ping()
    with conn.cursor() as cursor:         
        cursor.execute(sql, (email))
        results = cursor.fetchall()
    return results[0]['pass_hash']

def create_user(email, name, pass_hash):
    sql = """INSERT INTO user (email, name, pass_hash) VALUES (%s, %s, %s)"""
    # pinging connection with db, was getting some errors without this
    conn.ping()
    with conn.cursor() as cursor:         
        cursor.execute(sql, (email, name, pass_hash))
        conn.commit()

def select_products(category, num):
    sql = """SELECT pname, price, description, img_path FROM product WHERE category = %s ORDER BY popularity LIMIT %s"""
    with conn.cursor() as cursor:         
        cursor.execute(sql, (category, num))
        results = cursor.fetchall()
    return results

