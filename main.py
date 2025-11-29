from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from database import TariffPlan, API_db
from models import fetch_geo_analysis
import os
import secrets
from analyzer import WebsiteAnalyzer
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(16)

tariff_db = TariffPlan()
api_db = API_db()

YANDEX_API_KEY = "AQVN2E_gKuTJc_B1jb1gPQK4jAQiEbl5RZtSkmGU"
YANDEX_FOLDER_ID = "b1g80nc4mkh3lm4s25h7"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyzer')
def service():
    return render_template('service.html', results=None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_login = request.form.get('username')
        password = request.form.get('password')
        user_info = tariff_db.get_user_info(user_login)
        if user_info and user_info[1] == password:
            session['user_login'] = user_login
            session['tariff'] = user_info[2]
            return redirect(url_for('service'))
        else:
            return render_template('login.html', error='Неверный логин или пароль')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_login = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return render_template('register.html', error='Пароли не совпадают')
        success, message = tariff_db.register_user(user_login, password)
        if success:
            session['user_login'] = user_login
            session['tariff'] = 'Бесплатный'
            return redirect(url_for('service'))
        else:
            return render_template('register.html', error=message)

    return render_template('register.html')



@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if request.is_json:
            data = request.get_json()
            url = data.get('url', '').strip()
        else:
            url = request.form.get('url', '').strip()
        if not url:
            if request.is_json:
                return jsonify({'error': 'URL не может быть пустым'}), 400
            else:
                return render_template('service.html', results=None, error="URL не может быть пустым")

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        geo_data = fetch_geo_analysis(url)

        table = []
        for item in geo_data.get("metrics", []):
            table.append({
                "Метрика": item["name"].replace("_", " "),
                "Значение": item.get("value", "N/A"),
                "Оценка": item.get("score", "N/A"),
                "Описание": item.get("explanation", "Пояснение недоступно")
            })

        overall = geo_data.get("overall", {})
        table.append({
            "Метрика": "ОБЩАЯ ОЦЕНКА GEO",
            "Значение": overall.get("value", "N/A"),
            "Оценка": overall.get("score", "N/A"),
            "Описание": overall.get("recommendations", "Рекомендации недоступны")
        })

        website_results = WebsiteAnalyzer().analyze_website(url)

        combined_results = {
            "url": url,
            "load_time": f"{time.time():.2f} сек",
            "geo_analysis": table,
        }

        if isinstance(website_results, dict):
            combined_results.update(website_results)

        if request.is_json:
            response_data = {
                "success": True,
                "geo_table": table,
                "website_analysis": website_results
            }
            return jsonify(response_data)
        else:
            if "error" not in website_results:
                return render_template('service.html', results=combined_results, error=None)
            else:
                return render_template('service.html', results=None,
                                       error=website_results.get("error", "Неизвестная ошибка"))

    except Exception as e:
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        else:
            return render_template('service.html', results=None, error=str(e))



@app.route('/profile')
def profile():
    if 'user_login' not in session:
        return redirect(url_for('login'))

    user_info = tariff_db.get_user_info(session['user_login'])
    if user_info:
        user_data = {
            'login': user_info[0],
            'tariff': user_info[2],
            'end_date': user_info[3],
            'requests_used': user_info[4],
            'max_requests': user_info[5],
            'api_access': user_info[6]
        }
        return render_template('profile.html', user=user_data, session=session)

    return redirect(url_for('login'))


@app.route('/upgrade', methods=['POST'])
def upgrade_tariff():
    if 'user_login' not in session:
        return jsonify({'error': 'Требуется авторизация'}), 401

    data = request.get_json()
    tariff_name = data.get('tariff')

    success, message = tariff_db.purchase_tariff(session['user_login'], tariff_name)

    if success:
        session['tariff'] = tariff_name
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message})


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))




if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        tariff_db.shutdown()