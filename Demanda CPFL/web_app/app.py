import os
import sys
from flask import Flask, render_template, request, jsonify

_dir = os.path.dirname(os.path.abspath(__file__))
if _dir not in sys.path:
    sys.path.insert(0, _dir)

from core.ged119 import calcular as calc_ged119
from core.ged13 import calcular as calc_ged13

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ged119')
def ged119():
    return render_template('ged119.html')

@app.route('/ged13')
def ged13():
    return render_template('ged13.html')

@app.route('/api/ged119/calcular', methods=['POST'])
def api_ged119():
    try:
        dados = request.get_json()
        resultado = calc_ged119(dados)
        return jsonify({'success': True, 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged13/calcular', methods=['POST'])
def api_ged13():
    try:
        dados = request.get_json()
        resultado = calc_ged13(dados)
        return jsonify({'success': True, 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
