import tweepy
import re
from twilio.rest import Client
import random
import _thread
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


class StreamListener(tweepy.StreamListener):
    def onstatus(self, status):
        print(status)

    def on_direct_message(self, status):
        print("Listening")
        global otp
        text = status.direct_message['text']
        sender = status.direct_message['sender']['screen_name']
        class_msg = classify(text)
        if(class_msg == 'Initiation'):
            payment_details = parseText(text)
            payment_details['sender'] = sender
            _thread.start_new_thread(do_transaction, payment_details)
        elif(classify == 'OTP'):
            otp = int(text)
        else:
            api.send_direct_message(sender, "Invalid request")


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
    if(len(parseText(text)) != 0):
        return "Initiation"
    elif(len(text) == 6 and str.isdigit(text)):
        return "OTP"
    else:
        return "Garbage"


def do_transaction(payment_details):
    beneficiary_balance = get_balance(payment_details.get('beneficiary'))
    sender_balance = get_balance(payment_details.get('sender'))
    if(payment_details.get('amount') > sender_balance):
        api.send_direct_message(sender, "Amount exceeds balance")
    else:
        otp_code = random.randint(100000, 999999)
        message = client.messages.create(to='+917337097978', from_="+12013993398", body=otp_code)

    while(otp != otp_code):
        pass

    set_balance(payment_details.get('sender'), sender_balance - payment_details.get('amount'))
    set_balance(payment_details.get('beneficiary'), beneficiary_balance + payment_details.get('amount'))


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
    balance = None
    for row in cursor.fetchall():
    	balance = int(row[0])
    return balance


listener = StreamListener()
stream = tweepy.Stream(auth, listener)
stream.userstream()
