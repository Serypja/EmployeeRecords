from flask import Flask, redirect, url_for, session
from auth import auth_bp
from director import director_bp
from employee import employee_bp
from models import initialize_work_time_file
import socket
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Замените на случайный ключ

# Регистрация Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(director_bp)
app.register_blueprint(employee_bp)

# Инициализация файла с данными
initialize_work_time_file()

@app.route('/')
def home():
    """Главная страница - перенаправление в зависимости от роли"""
    if 'username' in session:
        if session['role'] == 'director':
            return redirect(url_for('director.director_dashboard'))
        else:
            return redirect(url_for('employee.employee_dashboard'))
    return redirect(url_for('auth.login'))

def get_local_ip():
    """Получение локального IP адреса"""
    try:
        # Создаем временное соединение чтобы узнать IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == '__main__':
    # Получаем локальный IP
    local_ip = get_local_ip()
    port = 5000
    
    print("\n" + "="*50)
    print("🚀 Сайт запущен!")
    print("="*50)
    print(f"📱 Локальный доступ: http://127.0.0.1:{port}")
    print(f"🌐 Сетевой доступ: http://{local_ip}:{port}")
    print("="*50)
    print("Чтобы остановить сервер, нажмите Ctrl+C")
    print("="*50 + "\n")
    
    # Запускаем сервер
    app.run(
        host='0.0.0.0',  # Принимать соединения со всех интерфейсов
        port=port,
        debug=True,
        threaded=True  # Обрабатывать несколько запросов одновременно
    )