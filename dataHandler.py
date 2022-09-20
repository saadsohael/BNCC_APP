import mysql.connector
import bcrypt


def update_primary_app_data(column_name, new_data):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="saad1122002",
        database="first_db"
    )

    cursor = db.cursor()
    cursor.execute(f"UPDATE primary_app_data SET {column_name} = (%s)", (new_data,))
    db.commit()
    db.close()


def query_primary_app_data():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="saad1122002",
        database="first_db"
    )

    cursor = db.cursor()
    cursor.execute("SELECT * FROM primary_app_data")
    data = []
    for v in cursor:
        data.append(v)

    db.close()

    return data[0]


def create_primary_app_data():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="saad1122002",
        database="first_db"
    )

    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS primary_app_data(
                    theme_color VARCHAR(255))""")
    db.commit()

    cursor.execute("SELECT theme_color FROM primary_app_data")

    theme = ''
    for v in cursor:
        theme = v
    if theme == '':
        cursor.execute("INSERT INTO primary_app_data VALUES('Light')")
        db.commit()

    db.close()


def create_admin():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="saad1122002",
        database="first_db"
    )

    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS admin_data(
                    admin_username VARCHAR(255),
                    admin_email VARCHAR(255),
                    admin_password_salt VARCHAR(255),
                    admin_password VARCHAR(255))""")
    db.commit()

    # Declaring our password
    password = b'AfiaAmin1844'

    # Adding the salt to password
    salt = bcrypt.gensalt()

    # Hashing the password
    hashed_password = bcrypt.hashpw(password, salt)

    cursor.execute("INSERT INTO admin_data VALUES ('AMINUL ISLAM', 'urdu1844@gmail.com', (%s), (%s))",
                   (salt, hashed_password,))
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
