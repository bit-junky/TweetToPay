import tweepy
import re
from twilio.rest import Client
import random
import sqlite3

consumer_key = 'NKHMeDZvNkJjZZtdp3dKrH7RH'
secret_key = 'B5tmJXiMnFpmsLpifsRQ8BjbUfjDU7CnPkxp32E2c1bNzuTncQ'

access_token = '935553457045377024-V2jZkpCvcWvdz0IH5UOdj0Pj6utqdr4'
access_token_secret = 'J6rYBx9Qh8tm4sCsCXtdIIjuXet5BwjGSEIzZiTGE4AQv'

auth = tweepy.OAuthHandler(consumer_key, secret_key)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
print('Connected!')

twilio_acct_sid = 'AC5243361e66dc7fc05424f03d091a21f3'
twilio_auth_token = 'b20fafbbb2f3f993969191a41f0d24d9'
client = Client(twilio_acct_sid, twilio_auth_token)

otp = None
otp_code = None
status = "complete"
glo_payment_details = {}

class StreamListener(tweepy.StreamListener):
    def onstatus(self, status):
        print(status)

    def on_direct_message(self, status):
        global otp
        global glo_payment_details
        text = status.direct_message['text']
        sender = status.direct_message['sender']['screen_name']
        print(text + "  " + sender)

        class_msg = classify(text)
        if(sender != 'tweettopaybot'):
            if(class_msg == 'Initiation'):
                payment_details = parseText(text)
                payment_details['sender'] = sender
                glo_payment_details = payment_details
                begin_transaction(payment_details)
            elif(class_msg == 'OTP'):
                end_transaction(glo_payment_details, int(text))
            else:
                api.send_direct_message(sender, text="Invalid request")

    def on_error(self, status):
        print(status)


def parseText(text):
    beneficiary_reg = re.findall(r'\B\@\w+', text)
    if(len(beneficiary_reg) != 0):
        beneficiary = beneficiary_reg[0][1:]
    amount_reg = re.findall(r'(Rs\w+)', text)
    if(len(amount_reg) != 0):
        amount = amount_reg[0][2:]
    if(len(beneficiary_reg) != 0 and len(amount_reg) != 0):
        return {'beneficiary': beneficiary, 'amount': float(amount)}
    else:
        return {}


def classify(text):
    response = ''
    if(len(parseText(text)) != 0):
        response = "Initiation"
    elif(len(text) == 6 and str.isdigit(text)):
        response = "OTP"
    else:
        response = "Garbage"
    print(response)
    return response


def do_transaction(payment_details):
    global otp
    beneficiary_balance = get_balance(payment_details.get('beneficiary'))
    sender_balance = get_balance(payment_details.get('sender'))
    sender = payment_details.get('sender')
    beneficiary = payment_details.get('beneficiary')
    amount = payment_details.get('amount')

    if(payment_details.get('amount') > sender_balance):
        api.send_direct_message(sender, text="Amount exceeds balance")
        return
    else:
        otp_code = random.randint(100000, 999999)
        message = client.messages.create(
            to='+917337097978', from_="+12013993398", body=otp_code)

    while(True):
        if(otp is None):
            continue
        else:
            break

    if(otp == otp_code):
        print("OTP Matched!")
        set_balance(sender, sender_balance - amount)
        set_balance(beneficiary, beneficiary_balance + amount)
        otp = None
    else:
        api.send_direct_message(
            sender, text="Incorrect OTP. Try new transaction.")


def begin_transaction(payment_details):
    global otp
    global status
    beneficiary_balance = get_balance(payment_details.get('beneficiary'))
    sender_balance = get_balance(payment_details.get('sender'))
    sender = payment_details.get('sender')
    beneficiary = payment_details.get('beneficiary')
    amount = payment_details.get('amount')

    if(amount > sender_balance):
        api.send_direct_message(sender, text="Amount exceeds balance")
        return
    else:
        otp = random.randint(100000, 999999)
        message = client.messages.create(
            to='+917337097978', from_="+12013993398", body=otp)
    status = "pending"


def end_transaction(payment_details, otp_c):
    global otp
    global status

    beneficiary_balance = get_balance(payment_details.get('beneficiary'))
    sender_balance = get_balance(payment_details.get('sender'))

    print("Beneficiary Balance: " + str(beneficiary_balance))
    print("Sender Balance:" + str(sender_balance))

    sender = payment_details.get('sender')
    beneficiary = payment_details.get('beneficiary')
    amount = payment_details.get('amount')
    if(status == "pending"):
        if(otp == otp_c):
            print("OTP Matched")
            set_balance(sender, sender_balance - amount)
            set_balance(beneficiary, beneficiary_balance + amount)
            api.send_direct_message(
                sender, text="Transaction successful.")
        else:
            api.send_direct_message(
                sender, text="Incorrect OTP. Try new transaction.")
    status = "complete"


def get_balance(handle):
    conn = sqlite3.connect('Linking Page/static/sqlite.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT Balance FROM Customers WHERE TwitterHandle = ?", (handle,))
    balance = None
    for row in cursor.fetchall():
        balance = float(row[0])
    return balance


def get_mobile(handle):
    conn = sqlite3.connect('Linking Page/static/sqlite.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT Mobile FROM Customers WHERE TwitterHandle = ?", (handle,))
    mobile = None
    for row in cursor.fetchall():
        mobile = int(row[0])
    return mobile


def set_balance(handle, amount):
    conn = sqlite3.connect('Linking Page/static/sqlite.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Customers SET Balance = ? WHERE TwitterHandle = ?", (amount, handle,))
    conn.commit()
    conn.close()


listener = StreamListener()
stream = tweepy.Stream(auth, listener)
stream.userstream()
