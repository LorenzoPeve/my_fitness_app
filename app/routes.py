from flask import Flask, render_template, request

from app import app
import db

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        # db.

        name = request.form.get('name')
        return render_template('submit.html', name=name)

    return render_template('index.html')



