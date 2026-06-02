import os
import sys
from flask import Flask, render_template, request, jsonify

_dir = os.path.dirname(os.path.abspath(__file__))
if _dir not in sys.path:
    sys.path.insert(0, _dir)

from core.ged119 import calcular as calc_ged119, calcular_transformador
from core.ged13 import calcular as calc_ged13
from core.projetos_db import listar_projetos, carregar_projeto, salvar_projeto, excluir_projeto

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

@app.route('/api/ged119/calcular_transformador', methods=['POST'])
def api_calcular_transformador():
    try:
        dados = request.get_json()
        resultado = calcular_transformador(dados)
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

# --- PROJECT MANAGEMENT API ---

@app.route('/api/projetos/listar', methods=['GET'])
def api_projetos_listar():
    try:
        projetos = listar_projetos()
        return jsonify({'success': True, 'data': projetos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/projetos/carregar/<int:projeto_id>', methods=['GET'])
def api_projetos_carregar(projeto_id):
    try:
        proj = carregar_projeto(projeto_id)
        if proj is None:
            return jsonify({'success': False, 'error': 'Projeto nao encontrado'}), 404
        return jsonify({'success': True, 'data': proj})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/projetos/salvar', methods=['POST'])
def api_projetos_salvar():
    try:
        dados = request.get_json()
        projeto_id = dados.get('id')
        novo_id = salvar_projeto(projeto_id, dados)
        return jsonify({'success': True, 'data': {'id': novo_id}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/projetos/excluir/<int:projeto_id>', methods=['DELETE'])
def api_projetos_excluir(projeto_id):
    try:
        excluir_projeto(projeto_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
