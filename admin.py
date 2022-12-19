import mysql.connector
import bcrypt

"""
when adding information to admin database just append the info to info_list in line 13.
also append the info to create admin arguments in line 17.
then add the information in cursor.execute() in line 27.
finally add the info to cursor.execute() values in line 51.
"""


def admin_info():
    info_list = ['Name', 'Email', 'Mobile', 'DOB', 'Address', 'Blood Group', 'Religion', 'Institution']
    return info_list


def create_admin(username, password, image_path, admin_name, email_address, mobile, dob, address, blood_group, religion,
                 institution):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="saad1122002",
        database="first_db"
    )

    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS admin_data(
                    admin_username VARCHAR(255),
                    admin_password_salt VARCHAR(255),
                    admin_password VARCHAR(255),
                    profile_photo MEDIUMBLOB,
                    admin_name VARCHAR(99),
                    admin_email VARCHAR(255),
                    admin_mobile VARCHAR(99),
                    admin_dob VARCHAR(99),
                    admin_address VARCHAR(255),
                    admin_blood_group VARCHAR(99),
                    admin_religion VARCHAR(99),
                    admin_institution VARCHAR(255))""")

    # Adding the salt to password
    salt = bcrypt.gensalt()

    # Hashing the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    adm_name = ' '.join(list(map(lambda x: x.lower().capitalize(), admin_name.split(" "))))

    profile_photo = img_binary_data(image_path)

    cursor.execute("INSERT INTO admin_data VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                   (username, salt, hashed_password, profile_photo, adm_name, email_address, mobile, dob, address,
                    blood_group, religion, institution))
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
    password = input('passwd : ')
    img_path = 'profile_photo.jpeg'
    other_info = []

    for v in admin_info():
        data = input(f"{v} : ")
        other_info.append(data)

    if len(img_binary_data(img_path)) <= 100000:
        create_admin(username, password, img_path, other_info[0], other_info[1], other_info[2], other_info[3],
                     other_info[4], other_info[5], other_info[6], other_info[7])
        print('admin created!')
    else:
        print('try again!')


