from dotenv import load_dotenv
from flask import Flask
import os
load_dotenv(override=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY'), 'utf-8'

from app import routes