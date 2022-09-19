import mysql.connector
import bcrypt


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
