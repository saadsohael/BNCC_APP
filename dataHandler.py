import mysql.connector
import bcrypt
import sqlite3


def update_app_data(table_name, column_name, new_data):
    if table_name == 'static_app_data':
        db = sqlite3.connect("app_data.db")
    else:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="saad1122002",
            database="first_db"
        )

    cursor = db.cursor()

    cursor.execute(f"UPDATE {table_name} SET {column_name} = (?)", (new_data,))
    db.commit()
    db.close()


def query_app_data(table_name):
    if table_name == 'static_app_data':
        db = sqlite3.connect("app_data.db")
    else:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="saad1122002",
            database="first_db"
        )

    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()
    db.close()
    for v in data:
        return v


def create_app_data():
    db = sqlite3.connect("app_data.db")

    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS static_app_data(theme_color text)""")
    db.commit()

    cursor.execute("SELECT theme_color FROM static_app_data")
    data = cursor.fetchall()

    theme = ''
    for v in data:
        theme = data
    if theme == '':
        cursor.execute("INSERT INTO static_app_data VALUES('Light')")
        db.commit()

    db.close()

    online_db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="saad1122002",
        database="first_db"
    )

    form_items = ["Name : ",
                  "Father's Name : ",
                  "Mother's Name : ",
                  "Permanent Address : ",
                  "Height : ",
                  "Width : ",
                  "Any Genetic Disorder : "]
    primary_application_form = repr(form_items)

    c = online_db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS dynamic_app_data(application_form VARCHAR(999))""")

    c.execute("SELECT application_form FROM dynamic_app_data")

    application_form_items = ''
    for v in c:
        application_form_items = v
    if application_form_items == '':
        c.execute("INSERT INTO dynamic_app_data VALUES(%s)", (primary_application_form,))
        online_db.commit()

    online_db.close()


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
