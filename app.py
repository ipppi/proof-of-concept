from crypt import crypt
from hmac import compare_digest
from secrets import token_bytes

from flask import Flask, redirect, request, url_for
from flask_login import (LoginManager, UserMixin, current_user,
                         login_required, login_user, logout_user)

with open('static/login.html') as f: LOGIN_HTML = f.read()
with open('static/register.html') as f: REGISTER_HTML = f.read()

app = Flask(__name__)
app.secret_key = token_bytes()
login_manager = LoginManager(app)
users = {}


class User(UserMixin):
    pass


def authenticate(username, password):
    if username not in users: return False
    digest = users[username]['password']
    return compare_digest(digest, crypt(password, digest))


@login_manager.user_loader
def load_user(username):
    if username not in users: return None
    user = User()
    user.id = username
    return user


@login_manager.request_loader
def load_request(request):
    username = request.form.get('username')
    is_authenticated = authenticate(username, request.form['password'])
    user = User()
    user.id, user.is_authenticated = username, is_authenticated
    return user


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET': return REGISTER_HTML
    username = request.form['username']
    password = crypt(request.form['password'])
    users[username] = {'password': password}
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET': return LOGIN_HTML
    username = request.form['username']
    if not authenticate(username, request.form['password']): return 'Bad login'
    user = User()
    user.id = username
    login_user(user)
    return redirect(url_for('protected'))


@app.route('/protected')
@login_required
def protected():
    return f'Logged in as: {current_user.id}'


@app.route('/logout')
def logout():
    logout_user()
    return 'Logged out'


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'
