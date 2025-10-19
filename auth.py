from flask import Blueprint, render_template, request, redirect, url_for, session
from models import verify_password, get_user_by_username

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if verify_password(username, password):
            user = get_user_by_username(username)
            session['username'] = username
            session['role'] = user['role']
            session['name'] = user['name']
            
            if user['role'] == 'director':
                return redirect(url_for('director.director_dashboard'))
            else:
                return redirect(url_for('employee.employee_dashboard'))
        else:
            return render_template('login/login.html', error='Неверный логин или пароль')
    
    return render_template('login/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))