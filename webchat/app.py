from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html', rasa_url=os.environ.get('RASA_URL'))