import json
import os
from datetime import datetime, timedelta

# База данных пользователей
users = {
    'director': {
        'password': 'director123',
        'role': 'director',
        'name': 'Иван Иванов'
    },
    'employee1': {
        'password': 'emp123',
        'role': 'employee',
        'name': 'Петр Петров'
    },
    'employee2': {
        'password': 'emp456',
        'role': 'employee',
        'name': 'Мария Сидорова'
    }
}

# Файл для хранения данных о рабочем времени
TIME_DATA_FILE = 'work_time_data.json'

def load_work_time_data():
    """Загрузка данных о рабочем времени"""
    try:
        if os.path.exists(TIME_DATA_FILE):
            with open(TIME_DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:  # Проверяем, что файл не пустой
                    return json.loads(content)
        # Если файла нет или он пустой, возвращаем пустой словарь
        return {}
    except (json.JSONDecodeError, Exception) as e:
        print(f"Ошибка загрузки данных: {e}")
        # Если произошла ошибка, возвращаем пустой словарь
        return {}

def save_work_time_data(data):
    """Сохранение данных о рабочем времени"""
    try:
        with open(TIME_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")

def get_today_key():
    """Получение ключа для сегодняшней даты"""
    return datetime.now().strftime('%Y-%m-%d')

def get_user_by_username(username):
    """Получение пользователя по логину"""
    return users.get(username)

def verify_password(username, password):
    """Проверка пароля пользователя"""
    user = get_user_by_username(username)
    return user and user['password'] == password

def initialize_work_time_file():
    """Инициализация файла с рабочим временем, если он не существует или поврежден"""
    if not os.path.exists(TIME_DATA_FILE):
        save_work_time_data({})
    else:
        # Проверяем, что файл содержит валидный JSON
        try:
            with open(TIME_DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    json.loads(content)
                else:
                    save_work_time_data({})
        except json.JSONDecodeError:
            # Если файл поврежден, пересоздаем его
            print("Файл с данными поврежден, создаем новый...")
            save_work_time_data({})