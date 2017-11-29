from flask import Flask, url_for, render_template, request, redirect, session
from flask_oauthlib.client import OAuth
import sqlite3

SECRET_KEY = 'development key'

app = Flask(__name__)
app.secret_key = SECRET_KEY
oauth = OAuth()
twitter = oauth.remote_app('twitter',
                           base_url='https://api.twitter.com/1/',
                           request_token_url='https://api.twitter.com/oauth/request_token',
                           access_token_url='https://api.twitter.com/oauth/access_token',
                           authorize_url='https://api.twitter.com/oauth/authorize',
                           consumer_key='NKHMeDZvNkJjZZtdp3dKrH7RH',
                           consumer_secret='B5tmJXiMnFpmsLpifsRQ8BjbUfjDU7CnPkxp32E2c1bNzuTncQ'
                           )


@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        username = request.form['username']
        pasword = request.form['password']
        app.logger.info(username)
        if(authenticate(username, pasword)):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return redirect(url_for('index'))


@app.route('/home')
def home():
    app.logger.info(is_linked(session.get('username')))
    return render_template('home.html', linked=is_linked(session.get('username')))


@app.route('/logintotwitter', methods=['GET', 'POST'])
def logintotwitter():
    return twitter.authorize(callback=url_for('afterlink'))


@app.route('/afterlink', methods=['GET', 'POST'])
@twitter.authorized_handler
def afterlink(resp):
    app.logger.info(session.get('username'))
    app.logger.info(resp['screen_name'])
    update_twitter(session.get('username'), resp['screen_name'])
    return redirect(url_for('home', linked=True))


def authenticate(username, password):
    conn = sqlite3.connect('static/sqlite.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Customers WHERE Username = ? AND Password = ?", (username, password))
    if(cursor.fetchone() is not None):
        return True
    else:
        return False
    conn.close()


def update_twitter(username, handle):
    conn = sqlite3.connect('static/sqlite.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Customers SET IsLinked = 1, TwitterHandle = ? WHERE Username = ?", (handle, username))
    conn.commit()
    conn.close()
    app.logger.info("Details updated")


def is_linked(username):
    conn = sqlite3.connect('static/sqlite.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Customers WHERE Username = ? AND IsLinked = 1", (username,))
    if(cursor.fetchone() is not None):
        return True
    else:
        return False
    conn.close()


if __name__ == '__main__':
    app.run(debug=True)
