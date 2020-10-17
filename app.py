from secrets import token_bytes

from flask import Flask, redirect, request, url_for
from flask_login import (LoginManager, UserMixin, current_user,
                         login_required, login_user, logout_user)

with open('static/login.html') as f: LOGIN_HTML = f.read()

app = Flask(__name__)
app.secret_key = token_bytes()
login_manager = LoginManager(app)
users = {'foo@bar.tld': {'password': 'secret'}}


class User(UserMixin):
    pass


@login_manager.user_loader
def load_user(email):
    if email not in users: return None
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def load_request(request):
    email = request.form.get('email')
    if email not in users: return None
    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always
    # compare password hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[email]['password']
    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return LOGIN_HTML

    email = request.form['email']
    if (email not in users
        or request.form['password'] != users[email]['password']):
        return 'Bad login'

    user = User()
    user.id = email
    login_user(user)
    return redirect(url_for('protected'))


@app.route('/protected')
@login_required
def protected():
    return 'Logged in as: ' + current_user.id


@app.route('/logout')
def logout():
    logout_user()
    return 'Logged out'


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'
