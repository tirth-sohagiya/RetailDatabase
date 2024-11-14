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

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             database='test',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

with connection:
    with connection.cursor() as cursor:
        sql = "SELECT * FROM User"
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
