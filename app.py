from flask import Flask, render_template, request, jsonify
from analyzer import WebsiteAnalyzer
import os

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form.get('url')
    results = WebsiteAnalyzer().analyze_website(url)
    if results and "error" not in results:
        return render_template('result.html', results=results, error=None)
    else:
        return render_template('result.html', results=None, error=results.get("error", "Неизвестная ошибка"))

if __name__ == '__main__':
    app.run(debug=True)
    