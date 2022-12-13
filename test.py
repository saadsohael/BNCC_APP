import requests

api_key = ""
email_address = ""
response = requests.get(
    "https://isitarealemail.com/api/email/validate",
    params={'email': email_address},
    headers={'Authorization': "Bearer " + api_key})

status = response.json()['status']
if status == "valid":
    print("email is valid")
elif status == "invalid":
    print("email is invalid")
