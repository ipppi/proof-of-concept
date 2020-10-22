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
from flask_login import LoginManager, UserMixin, login_user, logout_user

from .singletons import app, pg
from .static import login_html, register_html


class User(UserMixin):
    def __init__(self, username, is_maintainer):
        self.username = username
        self.is_maintainer = is_maintainer

    def get_id(self): return self.username


class AccountData:
    def __init__(self, pg):
        self.pg = pg
        pg.run(
            'CREATE TEMPORARY TABLE account ('
            ' username TEXT PRIMARY KEY, password TEXT,'
            ' maintainer BOOLEAN NOT NULL DEFAULT FALSE)')
        pg.run('INSERT INTO account (username, password, maintainer)'
               ' VALUES (:username, :password, true)',
               username='cnx', password=crypt('cnx'))

    def user_exists(self, username):
        return bool(self.pg.run(
            f"SELECT username FROM account WHERE username='{username}'"))

    def add(self, username, password):
        if self.user_exists(username): return False
        self.pg.run('INSERT INTO account (username, password)'
                    ' VALUES (:username, :password)',
                    username=username, password=crypt(password))
        return True

    def authenticate(self, username, password):
        passwords = self.pg.run(
            f"SELECT password FROM account WHERE username='{username}'")
        try:
            digest = passwords[0][0]
        except IndexError:
            return False
        else:
            return compare_digest(digest, crypt(password, digest))

    def __getitem__(self, username):
        is_maintainer = self.pg.run(
            f"SELECT maintainer FROM account WHERE username='{username}'")
        try:
            return User(username, is_maintainer[0][0])
        except IndexError:
            return None


login_manager = LoginManager(app)
accounts = AccountData(pg)


@login_manager.user_loader
def load_user(username):
    return accounts[username]


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET': return register_html
    if accounts.add(request.form['username'], request.form['password']):
        return redirect(url_for('index'))
    return 'username already exists'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET': return login_html
    username = request.form['username']
    if not accounts.authenticate(username, request.form['password']):
        return 'bad login'
    login_user(accounts[username])
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return 'logged out'


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'unauthorized'
