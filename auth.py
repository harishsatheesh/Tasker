from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app
from app import db
import time

auth = Blueprint("auth",__name__)

#Auth errors
class APIAuthError(Exception):
    code = 403
    description = "Authentication Error"

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(1000))
    name = db.Column(db.String(1000))

@auth.route("/signup",methods = ['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        Password = request.form.get('password')
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Email address already exists','error')
            return redirect(url_for('auth.signup'))

        # Create new user
        new_user = User(email=email, name=name, password=generate_password_hash(Password))
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('signup.html')

@auth.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first() 

        # Check if user exists and verify password
        if not user or not check_password_hash(user.password, password):
            flash('Invalid login credentials','error')
            return redirect(url_for('auth.login'))
        
        session['user_id'] = user.id
        session['user_name'] = user.name  

        # flash(f'Welcome, {user.name}!','success')
        return redirect(url_for('home'))


    return render_template('login.html')

@auth.route("/logout")
def logout():
    return redirect(url_for('auth.login'))