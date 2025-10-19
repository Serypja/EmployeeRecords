from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
from models import load_work_time_data, save_work_time_data, get_today_key

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/employee')
def employee_dashboard():
    if 'username' not in session or session['role'] != 'employee':
        return redirect(url_for('auth.login'))
    
    username = session['username']
    today_key = get_today_key()
    work_data = load_work_time_data()
    
    # Получаем данные за сегодня
    today_data = work_data.get(username, {}).get(today_key, {})
    
    # Получаем историю за последние 7 дней
    history = get_employee_history(username)
    
    return render_template('employee/employee.html', 
                         name=session['name'],
                         today_data=today_data,
                         history=history,
                         today_key=today_key)

@employee_bp.route('/start_work', methods=['POST'])
def start_work():
    if 'username' not in session or session['role'] != 'employee':
        return jsonify({'success': False, 'error': 'Не авторизован'})
    
    username = session['username']
    today_key = get_today_key()
    current_time = datetime.now().strftime('%H:%M')
    
    work_data = load_work_time_data()
    
    if username not in work_data:
        work_data[username] = {}
    
    # Если рабочий день уже начат, не позволяем начать снова
    if today_key in work_data[username] and work_data[username][today_key].get('status') == 'working':
        return jsonify({'success': False, 'error': 'Рабочий день уже начат'})
    
    work_data[username][today_key] = {
        'start_time': current_time,
        'end_time': '',
        'total_hours': '0',
        'status': 'working',
        'employee_name': session['name'],
        'description': '',  # Добавляем пустое описание
        'actual_start_time': current_time,  # Реальное время начала
        'actual_end_time': '',  # Реальное время окончания
        'edited_start_time': None,  # Когда редактировали время начала
        'edited_end_time': None,    # Когда редактировали время окончания
        'original_start_time': current_time,  # Оригинальное время начала
        'original_end_time': ''     # Оригинальное время окончания
    }
    
    save_work_time_data(work_data)
    
    return jsonify({'success': True, 'start_time': current_time})

@employee_bp.route('/end_work', methods=['POST'])
def end_work():
    if 'username' not in session or session['role'] != 'employee':
        return jsonify({'success': False, 'error': 'Не авторизован'})
    
    username = session['username']
    today_key = get_today_key()
    current_time = datetime.now().strftime('%H:%M')
    
    work_data = load_work_time_data()
    
    # Проверяем, был ли начат рабочий день
    if username not in work_data or today_key not in work_data[username]:
        return jsonify({'success': False, 'error': 'Рабочий день не был начат'})
    
    if work_data[username][today_key].get('status') != 'working':
        return jsonify({'success': False, 'error': 'Рабочий день уже завершен'})
    
    start_time_str = work_data[username][today_key]['start_time']
    start_time = datetime.strptime(start_time_str, '%H:%M')
    end_time = datetime.strptime(current_time, '%H:%M')
    
    # Вычисляем разницу во времени
    time_diff = end_time - start_time
    total_hours = round(time_diff.total_seconds() / 3600, 2)
    
    # Сохраняем описание перед обновлением
    existing_description = work_data[username][today_key].get('description', '')
    
    work_data[username][today_key].update({
        'end_time': current_time,
        'total_hours': str(total_hours),
        'status': 'completed',
        'actual_end_time': current_time,  # Сохраняем реальное время окончания
        'description': existing_description  # Сохраняем существующее описание
    })
    
    # Если это первое завершение, сохраняем оригинальное время окончания
    if not work_data[username][today_key].get('original_end_time'):
        work_data[username][today_key]['original_end_time'] = current_time
    
    save_work_time_data(work_data)
    
    return jsonify({
        'success': True, 
        'end_time': current_time, 
        'total_hours': total_hours
    })

@employee_bp.route('/update_work_time', methods=['POST'])
def update_work_time():
    if 'username' not in session or session['role'] != 'employee':
        return jsonify({'success': False, 'error': 'Не авторизован'})
    
    username = session['username']
    date = request.form.get('date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    description = request.form.get('description', '')  # Получаем описание
    
    if not all([date, start_time, end_time]):
        return jsonify({'success': False, 'error': 'Все поля обязательны'})
    
    try:
        # Вычисляем общее время
        start_dt = datetime.strptime(start_time, '%H:%M')
        end_dt = datetime.strptime(end_time, '%H:%M')
        
        if end_dt <= start_dt:
            return jsonify({'success': False, 'error': 'Время окончания должно быть позже времени начала'})
        
        time_diff = end_dt - start_dt
        total_hours = round(time_diff.total_seconds() / 3600, 2)
        
        work_data = load_work_time_data()
        
        if username not in work_data:
            work_data[username] = {}
        
        # Получаем текущие данные для сохранения реальных времен
        current_data = work_data[username].get(date, {})
        actual_start = current_data.get('actual_start_time', start_time)
        actual_end = current_data.get('actual_end_time', end_time)
        original_start = current_data.get('original_start_time', start_time)
        original_end = current_data.get('original_end_time', end_time)
        
        work_data[username][date] = {
            'start_time': start_time,
            'end_time': end_time,
            'total_hours': str(total_hours),
            'status': 'completed',
            'employee_name': session['name'],
            'description': description,
            'edited': True,
            'actual_start_time': actual_start,  # Сохраняем реальное время начала
            'actual_end_time': actual_end,      # Сохраняем реальное время окончания
            'edited_start_time': datetime.now().strftime('%Y-%m-%d %H:%M'),  # Когда редактировали
            'edited_end_time': datetime.now().strftime('%Y-%m-%d %H:%M'),    # Когда редактировали
            'original_start_time': original_start,  # Оригинальное время
            'original_end_time': original_end       # Оригинальное время
        }
        
        save_work_time_data(work_data)
        
        return jsonify({'success': True, 'total_hours': total_hours})
    
    except ValueError:
        return jsonify({'success': False, 'error': 'Неверный формат времени'})

@employee_bp.route('/update_description', methods=['POST'])
def update_description():
    """Обновление описания работы в реальном времени"""
    if 'username' not in session or session['role'] != 'employee':
        return jsonify({'success': False, 'error': 'Не авторизован'})
    
    username = session['username']
    date = request.form.get('date')
    description = request.form.get('description', '')
    
    if not date:
        return jsonify({'success': False, 'error': 'Дата не указана'})
    
    work_data = load_work_time_data()
    
    if username not in work_data:
        work_data[username] = {}
    
    if date not in work_data[username]:
        return jsonify({'success': False, 'error': 'Запись за указанную дату не найдена'})
    
    # Обновляем описание, сохраняя остальные данные
    work_data[username][date]['description'] = description
    save_work_time_data(work_data)
    
    return jsonify({'success': True})

def get_employee_history(username, days=7):
    """Получение истории работы сотрудника"""
    from datetime import timedelta
    
    work_data = load_work_time_data()
    history = []
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        day_data = work_data.get(username, {}).get(date, {})
        if day_data:
            history.append({
                'date': date,
                'start_time': day_data.get('start_time', '--:--'),
                'end_time': day_data.get('end_time', '--:--'),
                'total_hours': day_data.get('total_hours', '0'),
                'status': day_data.get('status', 'Не работал'),
                'description': day_data.get('description', ''),
                'actual_start_time': day_data.get('actual_start_time', '--:--'),
                'actual_end_time': day_data.get('actual_end_time', '--:--'),
                'edited': day_data.get('edited', False)
            })
    
    return history