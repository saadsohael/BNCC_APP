import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import bcrypt
import requests
import string
import mysql.connector
import threading as th

import dataHandler


def has_internet():
    url = "https://mail.google.com/"
    timeout = 5
    try:
        request = requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False


def send_pass_recovery_otp(toaddr):
    # generating otp
    letters = string.ascii_letters + str(random.randint(999, 999999))
    otp = ''.join(random.choice(letters) for i in range(6))
    otp_salt = bcrypt.gensalt()
    hashed_otp = bcrypt.hashpw(otp.encode('utf-8'), otp_salt)

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    if dataHandler.query_app_data('dynamic_app_data')[1] < 20:
        fromaddr = 'otp.manager1971@gmail.com'
        password = "qciibqknolujaalp"
    else:
        fromaddr = 'otp.manager1969@gmail.com'
        password = "asdf"

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

    # Authentication
    try:
        s.login(fromaddr, password)

        # Converts the Multipart msg into a string
        text = msg.as_string()

        # sending the mail
        s.sendmail(fromaddr, toaddr, text)

        db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="saad1122002",
            database="first_db"
        )

        cursor = db.cursor()

        cursor.execute("ALTER TABLE admin_data ADD otp_salt VARCHAR(99)")
        db.commit()
        cursor.execute("ALTER TABLE admin_data ADD otp VARCHAR(99)")
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

    return []


def mail_by_thread(toaddr):
    t1 = th.Thread(
        target=send_pass_recovery_otp,
        args=(toaddr,)
    )
    t1.start()
