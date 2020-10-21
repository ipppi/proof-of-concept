# Authentication
# Copyright (C) 2020  Nguyễn Gia Phong
#
# This file is part of IPPPI.
#
# IPPPI is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IPPPI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with IPPPI.  If not, see <https://www.gnu.org/licenses/>.

from crypt import crypt
from hmac import compare_digest

from flask import redirect, request, url_for
from flask_login import (LoginManager, UserMixin, current_user,
                         login_required, login_user, logout_user)

from .singletons import app, con
from .static import login_html, register_html


class AccountData:
    def __init__(self, con):
        self.con = con
        self.con.run(
            'CREATE TEMPORARY TABLE account (username TEXT, password TEXT)')

    def user_exists(self, username):
        return bool(self.con.run(
            f"SELECT username FROM account WHERE username='{username}'"))

    def add(self, username, password):
        if self.user_exists(username): return False
        con.run('INSERT INTO account (username, password)'
                ' VALUES (:username, :password)',
                username=username, password=crypt(password))
        return True

    def authenticate(self, username, password):
        passwords = self.con.run(
            f"SELECT password FROM account WHERE username='{username}'")
        try:
            digest = passwords[0][0]
        except IndexError:
            return False
        else:
            return compare_digest(digest, crypt(password, digest))


class User(UserMixin):
    def __init__(self, username):
        self.id = username


login_manager = LoginManager(app)
accounts = AccountData(con)


@login_manager.user_loader
def load_user(username):
    if not accounts.user_exists(username): return None
    return User(username)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET': return register_html
    if accounts.add(request.form['username'], request.form['password']):
        return redirect(url_for('login'))
    return 'username already exists'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET': return login_html
    username = request.form['username']
    if not accounts.authenticate(username, request.form['password']):
        return 'Bad login'
    login_user(User(username))
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