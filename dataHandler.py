import time
import mysql.connector
import bcrypt
import sqlite3


def update_app_data(table_name, column_name, new_data):
    if table_name == 'static_app_data':
        db = sqlite3.connect("app_data.db")
        cursor = db.cursor()

        cursor.execute(f"UPDATE {table_name} SET {column_name} = (?)", (new_data,))
        db.commit()
    else:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="saad1122002",
            database="first_db"
        )
        cursor = db.cursor()

        cursor.execute(f"UPDATE {table_name} SET {column_name} = (%s)", (new_data,))
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
                  "Email : "
                  "Father's Name : ",
                  "Mother's Name : ",
                  "Permanent Address : ",
                  "Height : ",
                  "Width : ",
                  "Any Genetic Disorder : "]
    primary_application_form = repr(form_items)

    c = online_db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS dynamic_app_data(
                application_form VARCHAR(999),
                otp_manager_1 INTEGER(99),
                otp_manager_2 INTEGER(99),
                otp_last_updated VARCHAR(255))""")
    online_db.commit()

    c.execute("SELECT application_form FROM dynamic_app_data")

    application_form_items = ''

    time_now = time.asctime()
    for v in c:
        application_form_items = v
    if application_form_items == '':
        c.execute("INSERT INTO dynamic_app_data VALUES(%s,0,0,%s)", (primary_application_form, time_now,))
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
    else:
        return False


def otp_matched(otp):
    otp_salt = query_admin('otp_salt')
    hash_otp = query_admin('otp')
    user_otp = (bcrypt.hashpw(otp.encode('utf-8'), otp_salt.encode('utf-8'))).decode('utf-8')
    if user_otp == hash_otp:
        return True
    else:
        return False


def query_admin(query):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="saad1122002",
        database="first_db"
    )

    cursor = db.cursor()
    cursor.execute(f"SELECT {query} FROM first_db.admin_data")
    data = None
    for v in cursor:
        data = v[0]
    db.close()
    return data


def drop_column(table_name, col_name):
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
    cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {col_name}")
    db.commit()


def mark_otp():
    db = sqlite3.connect('app_data.db')
    c = db.cursor()

    try:
        c.execute("ALTER TABLE static_app_data ADD COLUMN otp_sent_time")
        db.commit()
    except sqlite3.OperationalError:
        pass

    time_data = [v for v in time.asctime().split(" ") if v != '']
    time_data.remove(time_data[0])
    c.execute("UPDATE static_app_data SET otp_sent_time = (?)", (repr(time_data),))
    db.commit()
    db.close()


def otp_recently_sent(current_time_data):
    recently_sent = False

    try:
        month_now = current_time_data[1]
        date_now = current_time_data[2]
        hour_now = int(current_time_data[3].split(':')[0])
        year_now = current_time_data[4]

        db = sqlite3.connect("app_data.db")
        c = db.cursor()
        c.execute("SELECT otp_sent_time FROM static_app_data")
        prev_otp_time = eval(c.fetchall()[0][0])
        db.close()

        prev_month = prev_otp_time[0]
        prev_date = prev_otp_time[1]
        prev_hour = int(prev_otp_time[2].split(":")[0])
        prev_year = prev_otp_time[3]

        if year_now == prev_year:
            if month_now == prev_month:
                if date_now == prev_date:
                    recently_sent = True
                else:
                    if int(hour_now) <= prev_hour:
                        recently_sent = True
                    else:
                        recently_sent = False
            else:
                recently_sent = False
        else:
            recently_sent = False

    except sqlite3.OperationalError:
        recently_sent = False

    finally:
        return recently_sent


def update_otp_counter(command):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="saad1122002",
        database="first_db"
    )
    c = db.cursor()

    if command == 'increase':

        c.execute("SELECT otp_manager_1, otp_manager_2 FROM dynamic_app_data")

        otp_manager_1, otp_manager_2 = c.fetchall()[0]
        otp_manager_1_left = 20 - otp_manager_1
        otp_manager_2_left = 20 - otp_manager_2

        if otp_manager_1_left > 0:
            otp_manager_1 += 1
            c.execute("UPDATE dynamic_app_data SET otp_manager_1 = (%s)", (otp_manager_1,))
            db.commit()
        else:
            if otp_manager_2_left > 0:
                otp_manager_2 += 1
                c.execute("UPDATE dynamic_app_data SET otp_manager_2 = (%s)", (otp_manager_2,))
                db.commit()

    elif command == 'reset':
        c.execute("UPDATE dynamic_app_data SET otp_manager_1 = 0")
        db.commit()
        c.execute("UPDATE dynamic_app_data SET otp_manager_2 = 0")
        db.commit()


def set_database():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="saad1122002",
        database="first_db"
    )
    c = db.cursor()
    try:
        c.execute("ALTER TABLE admin_data DROP COLUMN otp_salt")
        db.commit()
        c.execute("ALTER TABLE admin_data DROP COLUMN otp")
        db.commit()
        db.close()

    except mysql.connector.errors.ProgrammingError:
        pass

    c.execute("SELECT otp_last_updated FROM dynamic_app_data")
    data = c.fetchall()[0][0]

    prev_day, prev_month, prev_date, prev_hour, prev_year = [v for v in data.split(" ") if v != '']
    day_now, month_now, date_now, hour_now, year_now = [v for v in time.asctime().split(" ") if v != '']

    if year_now == prev_year:
        if month_now == prev_month:
            if date_now == prev_date:
                pass
            else:
                if int(hour_now) <= int(prev_hour):
                    pass
                else:
                    update_otp_counter('reset')
        else:

            update_otp_counter('reset')
    else:
        update_otp_counter('reset')

# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     passwd="saad1122002",
#     database="first_db"
# )
# c = db.cursor()
# c.execute("UPDATE dynamic_app_data SET otp_manager_1 = 20")
# db.commit()
# c.execute("UPDATE dynamic_app_data SET otp_manager_2 = 20")
# db.commit()
