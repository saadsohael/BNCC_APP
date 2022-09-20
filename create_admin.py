import mysql.connector
import bcrypt


def create_admin(username, email_address, password, admin_name):
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
                    admin_password VARCHAR(255),
                    admin_name VARCHAR(50))""")

    # Adding the salt to password
    salt = bcrypt.gensalt()

    # Hashing the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    adm_name = ' '.join(list(map(lambda x: x.lower().capitalize(), admin_name.split(" "))))

    cursor.execute("INSERT INTO admin_data VALUES (%s,%s,%s,%s,%s)",
                   (username, email_address, salt, hashed_password, adm_name))
    db.commit()

    db.close()


# username = input('username : ')
# email_add = input('email : ')
# password = input('passwd : ')
# admin_name = input('name : ')

# create_admin(username, email_add, password, admin_name)
