import os
import sys
from flask import Flask, render_template, request, jsonify, session
from datetime import timedelta

_dir = os.path.dirname(os.path.abspath(__file__))
if _dir not in sys.path:
    sys.path.insert(0, _dir)

from core.ged119 import calcular as calc_ged119, calcular_transformador, calcular_poste, calcular_ramal_ligacao, get_tabela_ac, get_tabela4
from core.ramal import calcular_ramal, get_formas_agrupamento_nbr, calcular_neutro, get_tipos_eletroduto, calcular_eletroduto
from core.ged13 import calcular as calc_ged13, get_sugestao, get_conn as get_conn_g13
from core.ged2855 import calcular as calc_ged2855
import core.ged119 as ged119_mod
from core.projetos_db import listar_projetos, carregar_projeto, salvar_projeto, excluir_projeto
from core.projetos_ged13_db import listar_projetos as listar_projetos_g13, carregar_projeto as carregar_projeto_g13, salvar_projeto as salvar_projeto_g13, excluir_projeto as excluir_projeto_g13
from core.projetos_ged2855_db import listar_projetos as listar_projetos_g2855, carregar_projeto as carregar_projeto_g2855, salvar_projeto as salvar_projeto_g2855, excluir_projeto as excluir_projeto_g2855
from core.auth_db import autenticar, registrar_usuario, registrar_login, registrar_logout, listar_usuarios_com_estatisticas

app = Flask(__name__)
app.secret_key = 'cpfl-demanda-secret-key-change-in-production'
app.permanent_session_lifetime = timedelta(days=7)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/ged119')
def ged119():
    return render_template('ged119.html')

@app.route('/ged13')
def ged13():
    return render_template('ged13.html')

@app.route('/ged2855')
def ged2855():
    return render_template('ged2855.html')

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

@app.route('/api/ged119/calcular_poste', methods=['POST'])
def api_calcular_poste():
    try:
        dados = request.get_json()
        resultado = calcular_poste(dados)
        return jsonify({'success': True, 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged119/calcular_ramal', methods=['POST'])
def api_calcular_ramal():
    try:
        dados = request.get_json()
        resultado = calcular_ramal(dados)
        return jsonify({'success': True, 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged119/calcular_ramal_ligacao', methods=['POST'])
def api_calcular_ramal_ligacao():
    try:
        dados = request.get_json()
        resultado = calcular_ramal_ligacao(dados)
        return jsonify({'success': True, 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged119/calcular_neutro', methods=['POST'])
def api_calcular_neutro():
    try:
        dados = request.get_json()
        fase = float(dados.get('fase_mm2', 0))
        neutro = calcular_neutro(fase)
        return jsonify({'success': True, 'data': {'fase_mm2': fase, 'neutro_mm2': neutro}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged119/tipos_eletroduto', methods=['GET'])
def api_tipos_eletroduto():
    try:
        tipos = get_tipos_eletroduto()
        return jsonify({'success': True, 'data': tipos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged119/calcular_eletroduto', methods=['POST'])
def api_calcular_eletroduto():
    try:
        dados = request.get_json()
        resultado = calcular_eletroduto(
            dados['tipo_cabo'],
            float(dados['secao_mm2']),
            int(dados['n_condutores'])
        )
        return jsonify({'success': True, 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged119/formas_agrupamento_nbr', methods=['GET'])
def api_formas_agrupamento_nbr():
    try:
        formas = get_formas_agrupamento_nbr()
        return jsonify({'success': True, 'data': formas})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged119/formas_agrupamento', methods=['GET'])
def api_ged119_formas_agrupamento():
    try:
        formas = ged119_mod.get_formas_agrupamento()
        return jsonify({'success': True, 'data': formas})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged119/tabela2', methods=['GET'])
def api_ged119_tabela2():
    try:
        conn = ged119_mod.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TABELA_2")
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        conn.close()
        data = [dict(zip(cols, r)) for r in rows]
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged119/tabela_ac', methods=['GET'])
def api_ged119_tabela_ac():
    try:
        data = get_tabela_ac()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged119/tabela4', methods=['GET'])
def api_ged119_tabela4():
    try:
        data = get_tabela4()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged13/tabela8', methods=['GET'])
def api_ged13_tabela8():
    try:
        conn = get_conn_g13()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT btu_h, potencia_va, potencia_w FROM tabela8 ORDER BY btu_h")
        rows = cursor.fetchall()
        conn.close()
        data = [{'btu': r[0], 'va': r[1], 'w': r[2]} for r in rows]
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged13/sugestao', methods=['GET'])
def api_ged13_sugestao():
    try:
        area = float(request.args.get('area', 0))
        tipo = request.args.get('tipo', 'Residencial')
        resultado = get_sugestao(area, tipo)
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

# --- AUTH API ---
@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    try:
        dados = request.get_json()
        user, err = autenticar(dados.get('username', ''), dados.get('password', ''))
        if err: return jsonify({'success': False, 'error': err}), 401
        ip = request.remote_addr or ''
        ua = request.headers.get('User-Agent', '')
        log_id = registrar_login(user['id'], ip, ua)
        session.permanent = True
        session['user'] = user
        session['log_id'] = log_id
        return jsonify({'success': True, 'data': user})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/auth/register', methods=['POST'])
def api_auth_register():
    try:
        dados = request.get_json()
        user, err = registrar_usuario(
            dados.get('username', ''), dados.get('password', ''),
            dados.get('nome_completo', ''), dados.get('cidade', ''),
            dados.get('concessionaria', ''), dados.get('contato', '')
        )
        if err: return jsonify({'success': False, 'error': err}), 400
        return jsonify({'success': True, 'data': user})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/auth/logout', methods=['POST'])
def api_auth_logout():
    log_id = session.pop('log_id', None)
    session.pop('user', None)
    if log_id: registrar_logout(log_id)
    return jsonify({'success': True})

@app.route('/api/auth/me', methods=['GET'])
def api_auth_me():
    user = session.get('user')
    if not user: return jsonify({'success': False, 'error': 'Nao autenticado'}), 401
    return jsonify({'success': True, 'data': user})

# --- ADMIN API ---
@app.route('/api/admin/usuarios', methods=['GET'])
def api_admin_usuarios():
    user = session.get('user')
    if not user or not user.get('is_admin'): return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    data = listar_usuarios_com_estatisticas()
    return jsonify({'success': True, 'data': data})

@app.route('/api/admin/projetos/<int:usuario_id>', methods=['GET'])
def api_admin_projetos_usuario(usuario_id):
    user = session.get('user')
    if not user or not user.get('is_admin'): return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    proj119 = listar_projetos(usuario_id=usuario_id)
    proj13 = listar_projetos_g13(usuario_id=usuario_id)
    return jsonify({'success': True, 'data': {'ged119': proj119, 'ged13': proj13}})

# --- PROJECT MANAGEMENT API (GED-119) ---
@app.route('/api/projetos/listar', methods=['GET'])
def api_projetos_listar():
    try:
        user = session.get('user')
        if not user: return jsonify({'success': True, 'data': []})
        uid = None if user.get('is_admin') else user.get('id')
        projetos = listar_projetos(usuario_id=uid)
        return jsonify({'success': True, 'data': projetos})
    except Exception as e: return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/projetos/carregar/<int:projeto_id>', methods=['GET'])
def api_projetos_carregar(projeto_id):
    try: proj = carregar_projeto(projeto_id); return jsonify({'success': True, 'data': proj}) if proj else jsonify({'success': False, 'error': 'Projeto nao encontrado'}), 404
    except Exception as e: return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/projetos/salvar', methods=['POST'])
def api_projetos_salvar():
    try:
        user = session.get('user')
        if not user: return jsonify({'success': False, 'error': 'Faça login para salvar projetos'}), 401
        dados = request.get_json(); projeto_id = dados.get('id')
        uid = user.get('id')
        novo_id = salvar_projeto(projeto_id, dados, usuario_id=uid)
        return jsonify({'success': True, 'data': {'id': novo_id}})
    except Exception as e: return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/projetos/excluir/<int:projeto_id>', methods=['DELETE'])
def api_projetos_excluir(projeto_id):
    try:
        user = session.get('user')
        if not user: return jsonify({'success': False, 'error': 'Faça login para excluir projetos'}), 401
        excluir_projeto(projeto_id); return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': str(e)}), 400

# --- GED-2855 API ---
@app.route('/api/ged2855/calcular', methods=['POST'])
def api_ged2855():
    try:
        dados = request.get_json()
        resultado = calc_ged2855(dados)
        return jsonify({'success': True, 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# --- GED-2855 PROJECT MANAGEMENT API ---
@app.route('/api/ged2855/projetos/listar', methods=['GET'])
def api_ged2855_projetos_listar():
    try:
        user = session.get('user')
        if not user:
            projetos = listar_projetos_g2855(usuario_id=-1)
            return jsonify({'success': True, 'data': projetos})
        uid = None if user.get('is_admin') else user.get('id')
        projetos = listar_projetos_g2855(usuario_id=uid)
        return jsonify({'success': True, 'data': projetos})
    except Exception as e: return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged2855/projetos/carregar/<int:projeto_id>', methods=['GET'])
def api_ged2855_projetos_carregar(projeto_id):
    try: proj = carregar_projeto_g2855(projeto_id); return jsonify({'success': True, 'data': proj}) if proj else jsonify({'success': False, 'error': 'Projeto nao encontrado'}), 404
    except Exception as e: return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged2855/projetos/salvar', methods=['POST'])
def api_ged2855_projetos_salvar():
    try:
        user = session.get('user')
        if not user: return jsonify({'success': False, 'error': 'Faça login para salvar projetos'}), 401
        dados = request.get_json(); projeto_id = dados.get('id')
        uid = user.get('id')
        novo_id = salvar_projeto_g2855(projeto_id, dados, usuario_id=uid)
        return jsonify({'success': True, 'data': {'id': novo_id}})
    except Exception as e: return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged2855/projetos/excluir/<int:projeto_id>', methods=['DELETE'])
def api_ged2855_projetos_excluir(projeto_id):
    try:
        user = session.get('user')
        if not user: return jsonify({'success': False, 'error': 'Faça login para excluir projetos'}), 401
        excluir_projeto_g2855(projeto_id); return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': str(e)}), 400

# --- GED-13 PROJECT MANAGEMENT API ---
@app.route('/api/ged13/projetos/listar', methods=['GET'])
def api_ged13_projetos_listar():
    try:
        user = session.get('user')
        if not user: return jsonify({'success': True, 'data': []})
        uid = None if user.get('is_admin') else user.get('id')
        projetos = listar_projetos_g13(usuario_id=uid)
        return jsonify({'success': True, 'data': projetos})
    except Exception as e: return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged13/projetos/carregar/<int:projeto_id>', methods=['GET'])
def api_ged13_projetos_carregar(projeto_id):
    try: proj = carregar_projeto_g13(projeto_id); return jsonify({'success': True, 'data': proj}) if proj else jsonify({'success': False, 'error': 'Projeto nao encontrado'}), 404
    except Exception as e: return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged13/projetos/salvar', methods=['POST'])
def api_ged13_projetos_salvar():
    try:
        user = session.get('user')
        if not user: return jsonify({'success': False, 'error': 'Faça login para salvar projetos'}), 401
        dados = request.get_json(); projeto_id = dados.get('id')
        uid = user.get('id')
        novo_id = salvar_projeto_g13(projeto_id, dados, usuario_id=uid)
        return jsonify({'success': True, 'data': {'id': novo_id}})
    except Exception as e: return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ged13/projetos/excluir/<int:projeto_id>', methods=['DELETE'])
def api_ged13_projetos_excluir(projeto_id):
    try:
        user = session.get('user')
        if not user: return jsonify({'success': False, 'error': 'Faça login para excluir projetos'}), 401
        excluir_projeto_g13(projeto_id); return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
