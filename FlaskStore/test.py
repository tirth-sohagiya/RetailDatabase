"""import mysqlx

session = mysqlx.get_session({
    "host": "localhost",
    "port": 33060,
    "user": "root",
    "password": "root"
    })
schema = session.get_schema('retaildb')
result = session.sql("SELECT * FROM `retaildb`.`User`").execute()
print(schema)
for row in result.fetch_all():
    print("uid: {0}, email: {1}, name: {2}, phone: {3}".format(row["uid"], row["email"], row["name"], row["phone"]))

print(result.fetch_all())"""
import pymysql.cursors

connection = pymysql.connect(host='aws.cjwc228ggyr7.us-west-1.rds.amazonaws.com',
                             user='admin',
                             password='password',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

with connection:
    with connection.cursor() as cursor:
        sql = "CREATE DATABASE IF NOT EXISTS test"
        sql = "CREATE TABLE user (uid INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(40) NOT NULL, name VARCHAR(40) NOT NULL, pass VARCHAR(15) NOT NULL)"  
        cursor.execute(sql)
        #result = cursor.fetchall()
        #print(result)
        sql = "SELECT * FROM user"
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)
        
connection.ping()
with connection:
    with connection.cursor() as cursor:
        sql = """INSERT INTO user (email, name, pass) VALUES (%s, %s, %s)"""
        cursor.execute(sql, ('lucas@gmail.com', 'lucas', 'password'))
        result = cursor.fetchall()
        connection.commit()
        print(result)
