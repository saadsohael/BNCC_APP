import mysql.connector
import bcrypt
import sqlite3


def update_primary_app_data(column_name, new_data):
    db = sqlite3.connect("app_data.db")
    cursor = db.cursor()

    cursor.execute(f"UPDATE primary_app_data SET {column_name} = (?)", (new_data,))
    db.commit()
    db.close()


def query_primary_app_data():
    db = sqlite3.connect("app_data.db")

    cursor = db.cursor()
    cursor.execute("SELECT * FROM primary_app_data")
    data = cursor.fetchall()
    db.close()
    for v in data:
        return v


def create_primary_app_data():
    db = sqlite3.connect("app_data.db")

    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS primary_app_data(theme_color text)""")
    db.commit()

    cursor.execute("SELECT theme_color FROM primary_app_data")
    data = cursor.fetchall()

    theme = ''
    for v in data:
        theme = data
    if theme == '':
        cursor.execute("INSERT INTO primary_app_data VALUES('Light')")
        db.commit()

    db.close()


def is_admin(admin_username, admin_password):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="saad1122002",
        database="first_db"
    )

    cursor = db.cursor()
    cursor.execute("SELECT admin_username, admin_email, admin_password_salt, admin_password FROM first_db.admin_data")
    username = ''
    adm_email = ''
    pass_salt = ''
    passwd = ''
    for v in cursor:
        username = v[0]
        adm_email = v[1]
        pass_salt = v[2]
        passwd = v[3]

    hashed_pass = (bcrypt.hashpw(admin_password.encode('utf-8'), pass_salt.encode('utf-8'))).decode('utf-8')

    if admin_username == username or admin_username == adm_email:
        if hashed_pass == passwd:
            return True
    else:
        return False
