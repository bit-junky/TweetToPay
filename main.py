import tweepy
import re
from twilio.rest import Client

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


class StreamListener(tweepy.StreamListener):
    def onstatus(self, status):
        print(status)

    def on_direct_message(self, status):
        print(status.direct_message)
        text = status.direct_message['text']
        sender = status.direct_message['sender']['screen_name']
        payment_details = parseText(text)
        payment_details['sender'] = sender
        do_transaction(payment_details)
        message = client.messages.create(to="+917013841265", from_="+12013993398", body=text)


def parseText(text):
    beneficiary_reg = re.findall(r'\B\@\w+', text)
    beneficiary = beneficiary_reg[0][1:]
    amount_reg = re.findall(r'(Rs\w+)', text)
    amount = amount_reg[0][2:]
    return {'beneficiary': beneficiary, 'amount': amount}


def do_transaction(payment_details):
    pass


listener = StreamListener()
stream = tweepy.Stream(auth, listener)
stream.userstream()
