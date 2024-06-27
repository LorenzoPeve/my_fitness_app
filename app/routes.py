from functools import wraps
from flask import render_template, request, session, make_response
from flask import redirect, url_for
import os
import secrets

from app import app
from app import db

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('username'):
            return f(*args, **kwargs)
        return redirect(url_for('login'))

    return decorated

def get_csrf_token():
    return secrets.token_urlsafe(64)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == "GET":
        return render_template("register.html")
    
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if db.user_exists(username):
        return render_template(
            "register.html",
            invalid_message="Username already taken."
        )
    
    if db.email_exists(email):
        return render_template(
            "register.html",
            invalid_message="Email already taken."
        )

    db.add_user(username, password, email)
    return redirect('login')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "GET":
        return render_template("login.html")
    
    username = request.form.get("username")
    password = request.form.get("password")

    try:
        db.login_credentials_exists(username, password)
    except Exception as e:
        if 'User does not exist' in str(e):
            return render_template(
                "login.html",
                invalid_message="User does not exist. Please register."
            )
        elif 'Password does not match' in str(e):
            return render_template(
                "login.html",
                invalid_message="Incorrect password. Please try again."
            )
    else:
        session['username'] = username
        session['csrf_token'] = get_csrf_token()

    return redirect(url_for('my_records'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/my_records', methods=['GET', 'POST'])
@auth_required
def my_records():

    if request.method == "GET":
        if 'my_records_exercise' not in session:
            return render_template("records.html")
        
        records = db.get_weightlifting_records(
            session['username'],
            session['my_records_exercise'],
            session['my_records_reps']
        )
        return render_template("records.html", records=records)
    
    if request.form.get('csrf_token') != session['csrf_token']:
        return make_response("Invalid request. CSRF token authentication failed.", 400)
    
    records = db.get_weightlifting_records(
        session['username'],
        request.form.get('exercise'),
        request.form.get('n_reps')
    )

    session['my_records_exercise'] = request.form.get('exercise')
    session['my_records_reps'] = request.form.get('n_reps')

    return render_template("records.html", records=records)

@app.route('/delete_records', methods=['POST'])
@auth_required
def delete_records():

    if request.form.get('csrf_token') != session['csrf_token']:
        return make_response("Invalid request. CSRF token authentication failed.", 400)

    # Delete records
    ids = request.form.getlist('recs_delete')
    db.delete_exercise(ids, session['username'])
 
    return redirect(url_for('my_records'))