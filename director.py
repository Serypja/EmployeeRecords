from flask import Blueprint, render_template, session, redirect, url_for
from models import load_work_time_data, get_today_key, users
from datetime import datetime

director_bp = Blueprint('director', __name__)

@director_bp.route('/director')
def director_dashboard():
    if 'username' not in session or session['role'] != 'director':
        return redirect(url_for('auth.login'))
    
    work_data = load_work_time_data()
    
    # Получаем данные за сегодня
    today_key = get_today_key()
    today_work = {}
    for username, user_data in work_data.items():
        if today_key in user_data:
            today_work[username] = user_data[today_key]
            today_work[username]['username'] = username
    
    # Получаем общую статистику
    total_stats = calculate_total_stats(work_data)
    
    # Получаем историю редактирований
    edit_history = get_edit_history(work_data)
    
    return render_template('director/director.html', 
                         name=session['name'],
                         today_work=today_work,
                         total_stats=total_stats,
                         edit_history=edit_history,
                         today_key=today_key)

def calculate_total_stats(work_data):
    """Расчет общей статистики по всем сотрудникам"""
    total_stats = {}
    
    for username, user_data in work_data.items():
        total_hours = 0
        work_days = 0
        for day_data in user_data.values():
            if day_data.get('total_hours'):
                total_hours += float(day_data['total_hours'])
                work_days += 1
        
        total_stats[username] = {
            'total_hours': round(total_hours, 2),
            'work_days': work_days,
            'name': users.get(username, {}).get('name', 'Неизвестный')
        }
    
    return total_stats

def get_edit_history(work_data):
    """Получение истории редактирований времени"""
    edit_history = []
    
    for username, user_data in work_data.items():
        for date, day_data in user_data.items():
            if day_data.get('edited'):
                edit_history.append({
                    'username': username,
                    'employee_name': day_data.get('employee_name', 'Неизвестный'),
                    'date': date,
                    'current_start': day_data.get('start_time', '--:--'),
                    'current_end': day_data.get('end_time', '--:--'),
                    'original_start': day_data.get('original_start_time', '--:--'),
                    'original_end': day_data.get('original_end_time', '--:--'),
                    'actual_start': day_data.get('actual_start_time', '--:--'),
                    'actual_end': day_data.get('actual_end_time', '--:--'),
                    'edited_start_time': day_data.get('edited_start_time', 'Не редактировалось'),
                    'edited_end_time': day_data.get('edited_end_time', 'Не редактировалось'),
                    'total_hours': day_data.get('total_hours', '0')
                })
    
    # Сортируем по дате редактирования (новые сверху)
    edit_history.sort(key=lambda x: x.get('edited_start_time', ''), reverse=True)
    return edit_history