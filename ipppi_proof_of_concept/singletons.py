from secrets import token_bytes

from flask import Flask
from pg8000 import connect

app = Flask(__name__)
app.secret_key = token_bytes()
con = connect('postgres', password='postgres')
