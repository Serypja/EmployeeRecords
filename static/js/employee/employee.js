// Начать рабочий день
document.getElementById('startBtn').addEventListener('click', function() {
    fetch('/start_work', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Ошибка: ' + data.error);
            }
        });
});

// Завершить рабочий день
document.getElementById('endBtn').addEventListener('click', function() {
    fetch('/end_work', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Ошибка: ' + data.error);
            }
        });
});

// Редактирование времени
document.getElementById('editTimeForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    fetch('/update_work_time', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('editResult');
        if (data.success) {
            resultDiv.innerHTML = '<span class="success">✅ Время успешно обновлено! Общее время: ' + data.total_hours + ' часов</span>';
            setTimeout(() => location.reload(), 2000);
        } else {
            resultDiv.innerHTML = '<span class="error">❌ Ошибка: ' + data.error + '</span>';
        }
    });
});

// Сохранение описания
document.getElementById('descriptionFormElement').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    fetch('/update_description', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('descriptionResult');
        if (data.success) {
            resultDiv.innerHTML = '<span class="success">✅ Описание успешно сохранено!</span>';
            setTimeout(() => {
                resultDiv.innerHTML = '';
            }, 3000);
        } else {
            resultDiv.innerHTML = '<span class="error">❌ Ошибка: ' + data.error + '</span>';
        }
    });
});

// Автосохранение описания при изменении (опционально)
let descriptionTimeout;
document.getElementById('description').addEventListener('input', function() {
    clearTimeout(descriptionTimeout);
    descriptionTimeout = setTimeout(() => {
        const formData = new FormData(document.getElementById('descriptionFormElement'));
        fetch('/update_description', {
            method: 'POST',
            body: formData
        });
    }, 2000);
});

// Адаптивное меню для мобильных устройств
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем кнопку меню для мобильных
    if (window.innerWidth <= 768) {
        const header = document.querySelector('.header');
        const menuButton = document.createElement('button');
        menuButton.className = 'menu-toggle';
        menuButton.innerHTML = '☰';
        menuButton.style.cssText = `
            position: absolute;
            top: 15px;
            right: 15px;
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
        `;
        header.style.position = 'relative';
        header.appendChild(menuButton);
    }
});