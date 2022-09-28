import mysql.connector
import bcrypt


def create_admin(username, email_address, password, admin_name, image_path):
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
                    admin_name VARCHAR(50),
                    profile_photo MEDIUMBLOB)""")

    # Adding the salt to password
    salt = bcrypt.gensalt()

    # Hashing the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    adm_name = ' '.join(list(map(lambda x: x.lower().capitalize(), admin_name.split(" "))))

    profile_photo = img_binary_data(image_path)

    cursor.execute("INSERT INTO admin_data VALUES (%s,%s,%s,%s,%s, %s)",
                   (username, email_address, salt, hashed_password, adm_name, profile_photo))
    db.commit()

    db.close()


def update_password(new_pass):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="saad1122002",
        database="first_db"
    )

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_pass.encode('utf-8'), salt)

    c = db.cursor()
    c.execute("UPDATE admin_data SET admin_password_salt = (%s)", (salt,))
    db.commit()
    c.execute("UPDATE admin_data SET admin_password = (%s)", (hashed_password,))
    db.commit()
    db.close()


def img_binary_data(path):
    with open(path, 'rb') as imageFile:
        binary_data = imageFile.read()
    return binary_data


def fetch_admin_data():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="saad1122002",
        database="first_db"
    )

    c = db.cursor()

    c.execute("SELECT * FROM admin_data")
    for v in c:
        return v


def add_admin_to_database():
    username = input('username : ')
    email_add = input('email : ')
    password = input('passwd : ')
    admin_name = input('name : ')
    img_path = 'profile_photo.jpeg'

    if len(img_binary_data(img_path)) <= 100000:
        create_admin(username, email_add, password, admin_name, img_path)
        print('admin created!')
    else:
        print('try again!')
