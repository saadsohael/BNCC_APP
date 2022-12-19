import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import bcrypt
import requests
import string
import mysql.connector
import threading as th

import dataHandler


def gmail_id_pass():
    # storing the senders email address

    if dataHandler.query_app_data("otp_manager_1", "dynamic_app_data")[0][0] < 20:
        fromaddr = 'otp.manager1971@gmail.com'
        password = "qciibqknolujaalp"
    else:
        fromaddr = 'otp.manager1969@gmail.com'
        password = "bjyiyuqdbrogplfs"

    return fromaddr, password


def send_pass_recovery_otp(user, toaddr):
    # generating otp
    letters = string.ascii_letters + str(random.randint(999, 999999))
    otp = ''.join(random.choice(letters) for i in range(6))
    otp_salt = bcrypt.gensalt()
    hashed_otp = bcrypt.hashpw(otp.encode('utf-8'), otp_salt)
    print(otp)
    # instance of MIMEMultipart
    msg = MIMEMultipart()

    fromaddr, password = gmail_id_pass()

    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = 'OTP VERIFICATION (DO NOT REPLY)'

    # string to store the body of the mail
    body = f'Your OTP VERIFICATION CODE for BNCC APP is : {otp}\n\nDo not share it with anybody!'

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()
    if user == "admin":
        # Admin Authentication
        try:
            s.login(fromaddr, password)

            # Converts the Multipart msg into a string
            text = msg.as_string()

            # sending the mail to admin
            s.sendmail(fromaddr, toaddr, text)

            db = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="saad1122002",
                database="first_db"
            )

            cursor = db.cursor()

            cursor.execute("ALTER TABLE admin_data ADD COLUMN(otp_salt VARCHAR(99) DEFAULT 'N/A')")
            db.commit()
            cursor.execute("ALTER TABLE admin_data ADD COLUMN(otp VARCHAR(99) DEFAULT 'N/A')")
            db.commit()
            cursor.execute("UPDATE admin_data SET otp_salt = (%s)", (otp_salt,))
            db.commit()
            cursor.execute("UPDATE admin_data SET otp = (%s)", (hashed_otp,))
            db.commit()
            db.close()

        except:
            print("An Error occured while sending email.")
        finally:
            # terminating the session
            s.quit()
    else:
        # Cadet Authentication
        try:
            s.login(fromaddr, password)

            # Converts the Multipart msg into a string
            text = msg.as_string()

            # sending the mail to cadet
            s.sendmail(fromaddr, toaddr, text)

            db = sqlite3.connect("app_data.db")
            cursor = db.cursor()

            cursor.execute("ALTER TABLE cadet_offline_data ADD COLUMN cadet_email DEFAULT 'N/A'")
            db.commit()

            cursor.execute("INSERT INTO cadet_offline_data(cadet_email) VALUES(?)", (toaddr,))
            db.commit()

            cursor.execute("ALTER TABLE cadet_offline_data ADD COLUMN otp_salt DEFAULT 'N/A'")
            db.commit()

            cursor.execute("ALTER TABLE cadet_offline_data ADD COLUMN otp DEFAULT 'N/A'")
            db.commit()

            cursor.execute("UPDATE cadet_offline_data SET otp_salt = (?) WHERE cadet_email = (?)",
                           (otp_salt, toaddr))
            db.commit()

            cursor.execute("UPDATE cadet_offline_data SET otp = (?) WHERE cadet_email = (?)", (hashed_otp, toaddr))
            db.commit()
            db.close()

        except:
            print("An Error occured while sending email.")
        finally:
            # terminating the session
            s.quit()

    return []


def mail_by_thread(user, toaddr, target):
    t1 = th.Thread(
        target=target,
        args=(user, toaddr,)
    )
    t1.start()


def isValidEmail(email_address):
    api_key = ""
    response = requests.get(
        "https://isitarealemail.com/api/email/validate",
        params={'email': email_address},
        headers={'Authorization': "Bearer " + api_key})

    status = response.json()['status']
    if status == "valid":
        return True
    else:
        return False


def send_cadet_id_pass(no_use_argument, cadet_email):
    cadet_name = dataHandler.query_app_data('Name', 'cadet_application_data', 'Email', cadet_email)[0]
    cadet_unique_id = dataHandler.query_app_data('Cadet_Id', 'cadet_application_data', 'Email', cadet_email)[0]

    # generating password
    letters = string.ascii_letters + str(random.randint(999, 999999))
    cadet_unique_password = ''.join(random.choice(letters) for i in range(8))

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    fromaddr, password = gmail_id_pass()

    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = cadet_email

    # storing the subject
    msg['Subject'] = 'Cadet Login Id & Pass for RC BNCC APP'

    # string to store the body of the mail
    body = f'Congratulations {cadet_name[0]}! You have been chosen to be a Cadet. Your Cadet ID is {cadet_unique_id[0]}.\nYour RC BNCC APP User Id : {cadet_unique_id[0]}\nAnd RC BNCC Password : "{cadet_unique_password}"'

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    try:
        s.login(fromaddr, password)

        # Converts the Multipart msg into a string
        text = msg.as_string()

        # sending the mail
        s.sendmail(fromaddr, cadet_email, text)

        db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="saad1122002",
            database="first_db"
        )

        cursor = db.cursor()

        cursor.execute("UPDATE cadet_application_data SET Cadet_Password = (%s) WHERE Email = (%s)",
                       (cadet_unique_password, cadet_email))
        db.commit()
        db.close()

    except:
        print("An Error occurred while sending email.")

    finally:
        # terminating the session
        s.quit()

    return []


# mail_by_thread("admin", "rockdell420@gmail.com", send_pass_recovery_otp)
