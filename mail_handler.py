import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import requests
import string
import mysql.connector
import threading as th


def has_internet():
    url = "http://www.gmail.com"
    timeout = 5
    try:
        request = requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False


def send_pass_recovery_otp(send_to):
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        otp_manager_mail = 'otp.manager1971@gmail.com'
        otp_manager_pass = 'qciibqknolujaalp'

        smtp.login(otp_manager_mail, otp_manager_pass)

        letters = string.ascii_letters + str(random.randint(999, 999999))
        otp = ''.join(random.choice(letters) for i in range(6))

        db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="saad1122002",
            database="first_db"
        )

        cursor = db.cursor()

        cursor.execute("ALTER TABLE admin_data ADD otp VARCHAR(99)")
        cursor.execute("UPDATE admin_data SET otp = (%s)", (otp,))
        db.commit()
        db.close()

        subject = 'OTP VERIFICATION FOR PASSWORD(do_not_reply)'
        body = f'Your otp for RC BNCC Admin Login is : {otp}\nDo not share it with anyone.'
        msg = f'Subject: {subject}\n\n{body}'

        smtp.sendmail(otp_manager_mail, send_to, msg)


def SendEmail(toaddr):
    # generating otp
    letters = string.ascii_letters + str(random.randint(999, 999999))
    otp = ''.join(random.choice(letters) for i in range(6))

    # instance of MIMEMultipart
    msg = MIMEMultipart()
    # storing the senders email address
    fromaddr = 'otp.manager1971@gmail.com'
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = 'OTP VERIFICATION (DO NOT REPLY)'

    # string to store the body of the mail
    body = f'Your OTP VERIFICATION CODE for BNCC APP is : {otp}'

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    try:
        s.login(fromaddr, "qciibqknolujaalp")

        # Converts the Multipart msg into a string
        text = msg.as_string()

        # sending the mail
        s.sendmail(fromaddr, toaddr, text)
    except:
        print("An Error occured while sending email.")
    finally:
        # terminating the session
        s.quit()

    return []


def send_by_thread(toaddr):
    t1 = th.Thread(
        target=SendEmail,
        args=(toaddr)
    )
    t1.start()
