import math, io, base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, LogLocator

def calcular(dados):
    rtc_cliente = _n(dados.get('rtc_primario', 400)) / _n(dados.get('rtc_secundario', 5))
    rtc_cpfl = _n(dados.get('rtc_fase_cpfl', 120))
    curva_fase = _calc_curva_fase(dados)
    curva_fase_cliente = _gen_curva(dados.get('curva_fase_cliente', 'MI'), _n(dados.get('td_fase_cliente', 0.2)), _n(dados.get('tap_fase_cliente', 3)), rtc_cliente, i_min=1, i_max=20000, pontos=300)
    curva_neutro = _calc_curva_neutro(dados)
    curva_neutro_cliente = _gen_curva(dados.get('curva_neutro_cliente', 'NI'), _n(dados.get('td_neutro_cliente', 0.1)), _n(dados.get('tap_neutro_cliente', 0.25)), rtc_cliente, i_min=1, i_max=20000, pontos=300)
    curva_trafo = _calc_curva_trafo(dados)
    curva_inrush = _calc_curva_inrush(dados)
    result = {
        'itens': curva_fase,
        'itens_neutro': curva_neutro,
        'tcs': _calc_tc(dados),
        'relatorio': _gerar_relatorio(dados),
        'curva_fase': curva_fase,
        'curva_fase_cliente': curva_fase_cliente,
        'curva_neutro': curva_neutro,
        'curva_neutro_cliente': curva_neutro_cliente,
        'curva_trafo': curva_trafo,
        'curva_inrush': curva_inrush,
        'ponto_ansi': _calc_ponto_ansi(dados),
        'inrush_real': _calc_inrush_real(dados),
    }
    result['chart_fase'] = _gerar_chart_fase(curva_fase, curva_fase_cliente, curva_trafo, curva_inrush, dados)
    result['chart_neutro'] = _gerar_chart_neutro(curva_neutro, curva_neutro_cliente, dados)
    return result

def _n(v, default=0):
    try: return float(v) if v is not None and v != '' else default
    except: return default

def _calc_tc(dados):
    p_trafo = _n(dados.get('potencia_trafo', 1000))
    vff = _n(dados.get('tensao_suprimento', 13.8))
    rtc_prim = _n(dados.get('rtc_primario', 400))
    rtc_sec = _n(dados.get('rtc_secundario', 5))
    rtc = rtc_prim / rtc_sec
    in_ = p_trafo / (math.sqrt(3) * vff)
    inp = _n(dados.get('icc3f_assim', 7617)) / 20
    l_fiacao = _n(dados.get('comprimento_fiacao', 20))
    s_fiacao = _n(dados.get('secao_fiacao', 2.5))
    z_fiacao = 0.02 * l_fiacao / s_fiacao * 1000
    z_rele = _n(dados.get('z_rele', 13.2))
    z_tc = _n(dados.get('z_tc', 100))
    z_total = z_fiacao + z_rele + z_tc
    icc_max = _n(dados.get('icc_max_sistema', 10600))
    classe_tensao = dados.get('classe_tensao', '15kV')
    icc_sec = icc_max / rtc
    vsat = icc_sec * z_total / 1000
    carga_tc = _n(dados.get('carga_tc', 12.5))
    v_sat_max = 0.5 * (20 * rtc_sec)
    tc_ok = vsat <= v_sat_max
    return {
        'in': round(in_, 2),
        'inp': round(inp, 2),
        'rtc': round(rtc, 2),
        'rtc_str': f'{rtc_prim:.0f}/{rtc_sec:.0f}',
        'z_fiacao_mohm': round(z_fiacao, 2),
        'z_rele_mohm': round(z_rele, 2),
        'z_tc_mohm': round(z_tc, 2),
        'z_total_mohm': round(z_total, 2),
        'icc_sec_a': round(icc_sec, 2),
        'vsat_v': round(vsat, 2),
        'v_sat_max_v': round(v_sat_max, 2),
        'tc_ok': tc_ok,
        'carga_tc_va': carga_tc,
        'classe_tensao': classe_tensao,
        'icc_max_a': icc_max,
    }

def _curva_iec(tipo, td, ip, i_mult):
    if i_mult <= 1: return None
    m = i_mult - 1
    if tipo == 'MI':
        return td * (0.0515 / (pow(i_mult, 0.02) - 1) + 0.1140) if i_mult > 1 else None
    elif tipo == 'VI':
        return td * (13.5 / m) if m > 0 else None
    elif tipo == 'NI':
        return td * (0.14 / (pow(i_mult, 0.02) - 1)) if i_mult > 1 else None
    elif tipo == 'EI':
        return td * (80 / (i_mult * i_mult - 1)) if i_mult > 1 else None
    return None

def _gen_curva(tipo, td, ip, rtc, i_min=10, i_max=10000, pontos=200):
    pts = []
    for i in range(pontos):
        i_prim = i_min * math.pow(i_max / i_min, i / (pontos - 1))
        i_rel = i_prim / rtc
        i_mult = i_rel / ip
        t = _curva_iec(tipo, td, ip, i_mult)
        if t is not None and t > 0.001 and t < 10000:
            pts.append({'i': round(i_prim, 1), 't': round(t, 3)})
    return pts

def _calc_curva_fase(dados):
    return _gen_curva(
        dados.get('curva_fase_cpfl', 'VI'),
        _n(dados.get('td_fase_cpfl', 0.2)),
        _n(dados.get('tap_fase_cpfl', 5)),
        _n(dados.get('rtc_fase_cpfl', 120)),
        i_min=1, i_max=20000, pontos=300
    )

def _calc_curva_neutro(dados):
    return _gen_curva(
        dados.get('curva_neutro_cpfl', 'NI'),
        _n(dados.get('td_neutro_cpfl', 0.2)),
        _n(dados.get('tap_neutro_cpfl', 0.5)),
        _n(dados.get('rtc_fase_cpfl', 120)),
        i_min=1, i_max=20000, pontos=300
    )

def _calc_curva_trafo(dados):
    p_trafo = _n(dados.get('potencia_trafo', 1000))
    vff = _n(dados.get('tensao_suprimento', 13.8))
    z_trafo = _n(dados.get('z_trafo', 5))
    tolerancia = 1 + _n(dados.get('tolerancia_trafo', 0)) / 100
    in_nominal = p_trafo / (math.sqrt(3) * vff)
    i_ansi = in_nominal * (100 / z_trafo)
    pts = []
    pts.append({'i': in_nominal * tolerancia, 't': 10000})
    pts.append({'i': in_nominal * tolerancia, 't': 1800})
    pts.append({'i': i_ansi * 0.85, 't': 1800})
    pts.append({'i': i_ansi, 't': 3})
    pts.append({'i': i_ansi * 1.1, 't': 0.5})
    pts.append({'i': i_ansi * 2.0, 't': 0.02})
    return {'in_nominal': round(in_nominal, 2), 'i_ansi': round(i_ansi, 2), 'pontos': pts}

def _calc_curva_inrush(dados):
    p_trafo = _n(dados.get('potencia_trafo', 1000))
    vff = _n(dados.get('tensao_suprimento', 13.8))
    in_nominal = p_trafo / (math.sqrt(3) * vff)
    i_inrush = in_nominal * 10
    pts = []
    pts.append({'i': i_inrush, 't': 0.1})
    pts.append({'i': i_inrush, 't': 0.01})
    pts.append({'i': i_inrush * 0.5, 't': 0.5})
    pts.append({'i': i_inrush * 0.3, 't': 1.0})
    pts.append({'i': i_inrush * 0.1, 't': 10})
    return {'i_inrush': round(i_inrush, 2), 'pontos': pts}

def _calc_ponto_ansi(dados):
    p_trafo = _n(dados.get('potencia_trafo', 1000))
    vff = _n(dados.get('tensao_suprimento', 13.8))
    z_trafo = _n(dados.get('z_trafo', 5))
    in_nominal = p_trafo / (math.sqrt(3) * vff)
    i_ansi = in_nominal * (100 / z_trafo)
    return round(i_ansi, 2)

def _calc_inrush_real(dados):
    icc3f = _n(dados.get('icc3f_sim', 4735))
    p_trafo = _n(dados.get('potencia_trafo', 1000))
    vff = _n(dados.get('tensao_suprimento', 13.8))
    in_nominal = p_trafo / (math.sqrt(3) * vff)
    i_inrush = in_nominal * 10
    if icc3f + i_inrush > 0:
        i_real = 1 / (1 / icc3f + 1 / i_inrush)
    else:
        i_real = 0
    return round(i_real, 2)

def _gerar_relatorio(dados):
    tc = _calc_tc(dados)
    p_trafo = _n(dados.get('potencia_trafo', 1000))
    d_contratada = _n(dados.get('demanda_contratada', 900))
    vff = _n(dados.get('tensao_suprimento', 13.8))
    alimentador = dados.get('alimentador', '-')
    subestacao = dados.get('subestacao', '-')
    municipio = dados.get('municipio', '-')
    interessado = dados.get('interessado', '-')
    responsavel = dados.get('responsavel', '-')
    crea = dados.get('crea', '-')
    telefone = dados.get('telefone', '-')
    email = dados.get('email', '-')
    z_trafo = _n(dados.get('z_trafo', 5))
    in_nominal = p_trafo / (math.sqrt(3) * vff)
    inrush = in_nominal * 10
    inrush_real = _calc_inrush_real(dados)
    ponto_ansi = _calc_ponto_ansi(dados)
    icc3f_sim = _n(dados.get('icc3f_sim', 4735))
    icc3f_assim = _n(dados.get('icc3f_assim', 7617))
    icc2f_sim = _n(dados.get('icc2f_sim', 4101))
    icc2f_assim = _n(dados.get('icc2f_assim', 6596))
    iccft_zn0 = _n(dados.get('iccft_zn0', 3551))
    iccft_zn0_assim = _n(dados.get('iccft_zn0_assim', 5385))
    iccft_zn40 = _n(dados.get('iccft_zn40', 170))
    iccft_zn40_assim = _n(dados.get('iccft_zn40_assim', 173))
    rtc_fase = _n(dados.get('rtc_fase_cpfl', 120))
    rtc_prim = _n(dados.get('rtc_primario', 400))
    rtc_sec = _n(dados.get('rtc_secundario', 5))
    tap_fase_cpfl = _n(dados.get('tap_fase_cpfl', 5))
    curva_fase_cpfl = dados.get('curva_fase_cpfl', 'VI')
    td_fase_cpfl = _n(dados.get('td_fase_cpfl', 0.2))
    inst_fase_cpfl = _n(dados.get('inst_fase_cpfl', 32))
    tap_neutro_cpfl = _n(dados.get('tap_neutro_cpfl', 0.5))
    curva_neutro_cpfl = dados.get('curva_neutro_cpfl', 'NI')
    td_neutro_cpfl = _n(dados.get('td_neutro_cpfl', 0.2))
    inst_neutro_cpfl = _n(dados.get('inst_neutro_cpfl', 21))
    tap_51gs_cpfl = _n(dados.get('tap_51gs_cpfl', 0.1))
    td_51gs_cpfl = _n(dados.get('td_51gs_cpfl', 5))
    tap_fase_cliente = _n(dados.get('tap_fase_cliente', 3))
    curva_fase_cliente = dados.get('curva_fase_cliente', 'MI')
    td_fase_cliente = _n(dados.get('td_fase_cliente', 0.2))
    inst_fase_cliente = _n(dados.get('inst_fase_cliente', 23))
    tap_neutro_cliente = _n(dados.get('tap_neutro_cliente', 0.25))
    curva_neutro_cliente = dados.get('curva_neutro_cliente', 'NI')
    td_neutro_cliente = _n(dados.get('td_neutro_cliente', 0.1))
    inst_neutro_cliente = _n(dados.get('inst_neutro_cliente', 7.5))
    tap_51gs_cliente = _n(dados.get('tap_51gs_cliente', 0.1))
    td_51gs_cliente = _n(dados.get('td_51gs_cliente', 3))
    rtc_cliente = _n(dados.get('rtc_cliente', 80))

    return {
        'interessado': interessado,
        'responsavel': responsavel,
        'crea': crea,
        'telefone': telefone,
        'email': email,
        'carga_total': f'{p_trafo:.0f}kVA',
        'demanda_contratada': f'{d_contratada:.0f}kVA',
        'tensao_suprimento': f'{vff:.1f}kV',
        'alimentador': alimentador,
        'subestacao': subestacao,
        'municipio': municipio,
        'in_nominal': f'{in_nominal:.2f}A',
        'inrush': f'{inrush:.1f}A',
        'inrush_real': f'{inrush_real:.1f}A',
        'ponto_ansi': f'{ponto_ansi:.1f}A',
        'z_trafo': f'{z_trafo:.0f}%',
        'icc3f_sim': icc3f_sim, 'icc3f_assim': icc3f_assim,
        'icc2f_sim': icc2f_sim, 'icc2f_assim': icc2f_assim,
        'iccft_zn0': iccft_zn0, 'iccft_zn0_assim': iccft_zn0_assim,
        'iccft_zn40': iccft_zn40, 'iccft_zn40_assim': iccft_zn40_assim,
        'rtc_cpfl': f'{rtc_fase * rtc_sec:.0f}/{rtc_sec:.0f}',
        'ajustes_cpfl': {
            'fase': {'tap': tap_fase_cpfl, 'i_prim': round(tap_fase_cpfl * rtc_fase, 0), 'curva': curva_fase_cpfl, 'td': td_fase_cpfl, 'inst': inst_fase_cpfl, 'inst_prim': round(inst_fase_cpfl * rtc_fase, 0)},
            'neutro': {'tap': tap_neutro_cpfl, 'i_prim': round(tap_neutro_cpfl * rtc_fase, 1), 'curva': curva_neutro_cpfl, 'td': td_neutro_cpfl, 'inst': inst_neutro_cpfl, 'inst_prim': round(inst_neutro_cpfl * rtc_fase, 0)},
            '51gs': {'tap': tap_51gs_cpfl, 'i_prim': round(tap_51gs_cpfl * rtc_fase, 1), 'td': td_51gs_cpfl},
        },
        'rtc_cliente': f'{rtc_prim:.0f}/{rtc_sec:.0f}',
        'ajustes_cliente': {
            'fase': {'tap': tap_fase_cliente, 'i_prim': round(tap_fase_cliente * rtc_cliente, 0), 'curva': curva_fase_cliente, 'td': td_fase_cliente, 'inst': inst_fase_cliente, 'inst_prim': round(inst_fase_cliente * rtc_cliente, 0)},
            'neutro': {'tap': tap_neutro_cliente, 'i_prim': round(tap_neutro_cliente * rtc_cliente, 1), 'curva': curva_neutro_cliente, 'td': td_neutro_cliente, 'inst': inst_neutro_cliente, 'inst_prim': round(inst_neutro_cliente * rtc_cliente, 0)},
            '51gs': {'tap': tap_51gs_cliente, 'i_prim': round(tap_51gs_cliente * rtc_cliente, 1), 'td': td_51gs_cliente},
        },
        'tc': {
            'in': tc['in'], 'inp': tc['inp'],
            'rtc_str': tc['rtc_str'],
            'z_fiacao': tc['z_fiacao_mohm'], 'z_rele': tc['z_rele_mohm'],
            'z_tc': tc['z_tc_mohm'], 'z_total': tc['z_total_mohm'],
            'icc_sec': tc['icc_sec_a'], 'vsat': tc['vsat_v'],
            'v_sat_max': tc['v_sat_max_v'], 'tc_ok': tc['tc_ok'],
            'carga_va': tc['carga_tc_va'],
        }
    }

def _fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return b64

def _gerar_curva_definida(pickup_a, pickup_t, cur_max):
    x_vert = [pickup_a, pickup_a]
    y_vert = [1000, pickup_t]
    n = 100
    x_horiz = [pickup_a + (cur_max - pickup_a) * i / (n - 1) for i in range(n)]
    y_horiz = [pickup_t] * n
    return x_vert + x_horiz, y_vert + y_horiz

def _gerar_chart_fase(curva_fase, curva_cliente, curva_trafo, curva_inrush, dados=None):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_facecolor('#FFFBF5')

    rtc_cpfl = _n(dados.get('rtc_fase_cpfl', 120)) if dados else 120
    rtc_cliente = _n(dados.get('rtc_primario', 400)) / _n(dados.get('rtc_secundario', 5)) if dados else 80
    tensao = dados.get('tensao_suprimento', '13.8') if dados else '13.8'
    classe = dados.get('classe_tensao', '15kV') if dados else '15kV'
    tap_cpfl = _n(dados.get('tap_fase_cpfl', 5)) if dados else 5
    td_cpfl = _n(dados.get('td_fase_cpfl', 0.2)) if dados else 0.2
    inst_cpfl = _n(dados.get('inst_fase_cpfl', 32)) if dados else 32
    curva_cpfl = dados.get('curva_fase_cpfl', 'VI') if dados else 'VI'
    tap_cliente = _n(dados.get('tap_fase_cliente', 3)) if dados else 3
    td_cliente = _n(dados.get('td_fase_cliente', 0.2)) if dados else 0.2
    inst_cliente = _n(dados.get('inst_fase_cliente', 23)) if dados else 23
    curva_cliente_txt = dados.get('curva_fase_cliente', 'MI') if dados else 'MI'
    p_trafo = _n(dados.get('potencia_trafo', 1000)) if dados else 1000
    z_trafo = _n(dados.get('z_trafo', 5)) if dados else 5

    pickup_cpfl = tap_cpfl * rtc_cpfl
    inst_prim_cpfl = inst_cpfl * rtc_cpfl
    pickup_cliente = tap_cliente * rtc_cliente
    inst_prim_cliente = inst_cliente * rtc_cliente

    cur_plot_max = 10000.0

    if curva_fase:
        xs = [p['i'] for p in curva_fase]
        ys = [p['t'] for p in curva_fase]
        xs_m = [x for x in xs if x < inst_prim_cpfl]
        ys_m = [y for x, y in zip(xs, ys) if x < inst_prim_cpfl]
        if xs_m:
            ax.plot(xs_m, ys_m, color='blue', linewidth=3.5)
            ax.vlines(x=inst_prim_cpfl, ymin=0.02, ymax=ys_m[-1], colors='blue', linewidth=3.5)
            ax.hlines(y=0.02, xmin=inst_prim_cpfl, xmax=cur_plot_max, colors='blue', linewidth=3.5)
    if curva_cliente:
        xs = [p['i'] for p in curva_cliente]
        ys = [p['t'] for p in curva_cliente]
        xs_m = [x for x in xs if x < inst_prim_cliente]
        ys_m = [y for x, y in zip(xs, ys) if x < inst_prim_cliente]
        if xs_m:
            ax.plot(xs_m, ys_m, color='red', linewidth=3.5)
            ax.vlines(x=inst_prim_cliente, ymin=0.02, ymax=ys_m[-1], colors='red', linewidth=3.5)
            ax.hlines(y=0.02, xmin=inst_prim_cliente, xmax=cur_plot_max, colors='red', linewidth=3.5)
    if curva_trafo and curva_trafo.get('pontos'):
        xs = [p['i'] for p in curva_trafo['pontos']]
        ys = [p['t'] for p in curva_trafo['pontos']]
        ax.plot(xs, ys, color='black', linewidth=3.5)
    if curva_inrush and curva_inrush.get('pontos'):
        xs = [p['i'] for p in curva_inrush['pontos']]
        ys = [p['t'] for p in curva_inrush['pontos']]
        ax.plot(xs, ys, color='#10b981', linewidth=2, linestyle=':')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.5, 10000)
    ax.set_ylim(0.01, 1000)
    ax.xaxis.set_major_formatter(FormatStrFormatter('%g'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%g'))
    ax.grid(True, which='both', color='#90EE90', linestyle='-', linewidth=0.6)
    ax.tick_params(which='both', labelsize=9)
    ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=5))
    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=6))
    ax.set_title('8- Coordenograma - Gráfico Tempo x Corrente\n', fontsize=12, fontweight='bold', loc='left')
    ax.set_xlabel(f'Current in Amperes x 1 at {tensao} kV', fontsize=10)
    ax.set_ylabel('Time in Seconds', fontsize=10)
    ax.xaxis.set_label_position('top')

    ax.text(0.5, 0.5, 'Cópia Não Controlada', transform=ax.transAxes, fontsize=35, color='grey', alpha=0.15, ha='center', va='center', rotation=30)

    bbox_base = dict(boxstyle='square,pad=0.3', fc='white', ec='black', lw=1)
    bbox_cpfl = dict(boxstyle='square,pad=0.3', fc='white', ec='blue', lw=1)
    bbox_cliente = dict(boxstyle='square,pad=0.3', fc='white', ec='red', lw=1)

    txt_trafo = (f'Two-Winding Transformer (TR CLIENTE)\n'
                 f'Impedance: {z_trafo:.2f} [%]\n'
                 f'Rating: {p_trafo:.2f} [kVA]\n'
                 f'Voltage: {tensao} [kV]')
    ax.text(15, 30, txt_trafo, bbox=bbox_base, fontsize=8.5, color='black')

    txt_cpfl = (f'Overcurrent Relay - Electronic (FASE CPFL)\n'
                f'SIEMENS 7SJ600 {curva_cpfl}\n'
                f'Tap Range: [0.25 / 12.0] Tap: {tap_cpfl:.2f}\n'
                f'Pickup: {pickup_cpfl:.2f}[A] TD: {td_cpfl}\n'
                f'Inst. List (Pickup, Delay): ({inst_prim_cpfl:.1f}, 0.00)')
    ax.text(12, 2.5, txt_cpfl, bbox=bbox_cpfl, fontsize=8.5, color='blue')
    ax.annotate('', xy=(pickup_cpfl * 1.5, 4), xytext=(pickup_cpfl * 0.7, 4),
                arrowprops=dict(arrowstyle='->', color='blue'))

    txt_cliente = (f'Overcurrent Relay - Electronic (FASE CLIENTE)\n'
                   f'SIEMENS 7SJ6X {curva_cliente_txt}\n'
                   f'Tap Range: [0.25 / 12.0] Tap: {tap_cliente:.2f}\n'
                   f'Pickup: {pickup_cliente:.2f}[A] TD: {td_cliente}\n'
                   f'Inst. List (Pickup, Delay): ({inst_prim_cliente:.1f}, 0.00)')
    ax.text(5, 0.2, txt_cliente, bbox=bbox_cliente, fontsize=8.5, color='red')
    ax.annotate('', xy=(pickup_cliente * 1.5, 0.5), xytext=(pickup_cliente * 0.7, 0.5),
                arrowprops=dict(arrowstyle='->', color='red'))

    plt.figtext(0.5, 0.02, f"Figura A. Coordenograma de Fase - CPFL x Cliente ({tensao} kV).", ha="center", fontsize=11)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    return 'data:image/png;base64,' + _fig_to_b64(fig)


def _gerar_chart_neutro(curva_neutro, curva_cliente, dados=None):
    fig, ax = plt.subplots(figsize=(10, 12))
    ax.set_facecolor('#FFFBF5')

    rtc_cpfl = _n(dados.get('rtc_fase_cpfl', 120)) if dados else 120
    rtc_cliente = _n(dados.get('rtc_primario', 400)) / _n(dados.get('rtc_secundario', 5)) if dados else 80
    tensao = dados.get('tensao_suprimento', '13.8') if dados else '13.8'
    classe = dados.get('classe_tensao', '15kV') if dados else '15kV'

    tap_51gs_cpfl = _n(dados.get('tap_51gs_cpfl', 0.1)) if dados else 0.1
    td_51gs_cpfl = _n(dados.get('td_51gs_cpfl', 5)) if dados else 5
    tap_neutro_cpfl = _n(dados.get('tap_neutro_cpfl', 0.5)) if dados else 0.5
    td_neutro_cpfl = _n(dados.get('td_neutro_cpfl', 0.2)) if dados else 0.2
    inst_neutro_cpfl = _n(dados.get('inst_neutro_cpfl', 21)) if dados else 21
    curva_neutro_cpfl_txt = dados.get('curva_neutro_cpfl', 'NI') if dados else 'NI'

    tap_51gs_cliente = _n(dados.get('tap_51gs_cliente', 0.1)) if dados else 0.1
    td_51gs_cliente = _n(dados.get('td_51gs_cliente', 3)) if dados else 3
    tap_neutro_cliente = _n(dados.get('tap_neutro_cliente', 0.25)) if dados else 0.25
    td_neutro_cliente = _n(dados.get('td_neutro_cliente', 0.1)) if dados else 0.1
    inst_neutro_cliente = _n(dados.get('inst_neutro_cliente', 7.5)) if dados else 7.5
    curva_neutro_cliente_txt = dados.get('curva_neutro_cliente', 'NI') if dados else 'NI'

    pickup_51gs_cpfl = tap_51gs_cpfl * rtc_cpfl
    pickup_neutro_cpfl = tap_neutro_cpfl * rtc_cpfl
    inst_prim_cpfl = inst_neutro_cpfl * rtc_cpfl
    pickup_51gs_cliente = tap_51gs_cliente * rtc_cliente
    pickup_neutro_cliente = tap_neutro_cliente * rtc_cliente
    inst_prim_cliente = inst_neutro_cliente * rtc_cliente

    cur_plot_max = 10000.0

    # --- CPFL 51GS (Definite Time) ---
    i_dt_cpfl, t_dt_cpfl = _gerar_curva_definida(pickup_51gs_cpfl, td_51gs_cpfl, cur_plot_max)
    ax.plot(i_dt_cpfl, t_dt_cpfl, color='blue', linewidth=3.5)

    # --- CPFL Neutro (Inverse IEC + instantâneo) ---
    if curva_neutro:
        xs = [p['i'] for p in curva_neutro]
        ys = [p['t'] for p in curva_neutro]
        xs_m = [x for x in xs if x < inst_prim_cpfl]
        ys_m = [y for x, y in zip(xs, ys) if x < inst_prim_cpfl]
        if xs_m:
            ax.plot(xs_m, ys_m, color='blue', linewidth=3.5)
            ax.vlines(x=inst_prim_cpfl, ymin=0.02, ymax=ys_m[-1], colors='blue', linewidth=3.5)
            ax.hlines(y=0.02, xmin=inst_prim_cpfl, xmax=cur_plot_max, colors='blue', linewidth=3.5)

    # --- Cliente 51GS (Definite Time) ---
    i_dt_cli, t_dt_cli = _gerar_curva_definida(pickup_51gs_cliente, td_51gs_cliente, cur_plot_max)
    ax.plot(i_dt_cli, t_dt_cli, color='red', linewidth=3.5)

    # --- Cliente Neutro (Inverse IEC + instantâneo) ---
    if curva_cliente:
        xs = [p['i'] for p in curva_cliente]
        ys = [p['t'] for p in curva_cliente]
        xs_m = [x for x in xs if x < inst_prim_cliente]
        ys_m = [y for x, y in zip(xs, ys) if x < inst_prim_cliente]
        if xs_m:
            ax.plot(xs_m, ys_m, color='red', linewidth=3.5)
            ax.vlines(x=inst_prim_cliente, ymin=0.02, ymax=ys_m[-1], colors='red', linewidth=3.5)
            ax.hlines(y=0.02, xmin=inst_prim_cliente, xmax=cur_plot_max, colors='red', linewidth=3.5)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.5, 10000)
    ax.set_ylim(0.01, 1000)
    ax.xaxis.set_major_formatter(FormatStrFormatter('%g'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%g'))
    ax.grid(True, which='both', color='#90EE90', linestyle='-', linewidth=0.6)
    ax.tick_params(which='both', labelsize=9)
    ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=5))
    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=6))

    ax.set_title('8- Coordenograma - Gráfico Tempo x Corrente\n', fontsize=12, fontweight='bold', loc='left')
    ax.set_xlabel(f'Current in Amperes x 1 at {tensao} kV', fontsize=10)
    ax.set_ylabel('Time in Seconds', fontsize=10)
    ax.xaxis.set_label_position('top')

    ax.text(0.5, 0.5, 'Cópia Não Controlada', transform=ax.transAxes, fontsize=35, color='grey', alpha=0.15, ha='center', va='center', rotation=30)

    b_box = dict(boxstyle='square,pad=0.3', fc='white', ec='blue', lw=1)
    r_box = dict(boxstyle='square,pad=0.3', fc='white', ec='red', lw=1)

    txt_dt_cpfl = (f"Overcurrent Relay - Definite Time (51GS CPFL)\n"
                   f"Pickup Time:{td_51gs_cpfl:.2f}[s]\n"
                   f"Tap:{tap_51gs_cpfl:.2f}\n"
                   f"Pickup:{pickup_51gs_cpfl:.2f}[A]")
    ax.text(0.6, 600, txt_dt_cpfl, bbox=b_box, fontsize=8.5, color='blue', va='top')
    ax.annotate('', xy=(pickup_51gs_cpfl, 300), xytext=(5.5, 450), arrowprops=dict(arrowstyle='->', color='blue'))

    txt_elec_cpfl = (f"Overcurrent Relay - Electronic (Neutro CPFL)\n"
                     f"SIEMENS 7SJ600 IEC I\n"
                     f"Tap Range:[0.25 / 12.0] Tap:{tap_neutro_cpfl:.2f}\n"
                     f"Pickup:{pickup_neutro_cpfl:.2f}[A] TD:{td_neutro_cpfl}\n"
                     f"Inst. List (Pickup, Delay):({inst_prim_cpfl:.1f}, 0.00)")
    ax.text(0.6, 180, txt_elec_cpfl, bbox=b_box, fontsize=8.5, color='blue', va='top')
    ax.annotate('', xy=(pickup_neutro_cpfl * 1.5, 15), xytext=(5.5, 60), arrowprops=dict(arrowstyle='->', color='blue'))

    txt_dt_cli = (f"Overcurrent Relay - Definite Time (51GS Cliente)\n"
                  f"Pickup Time:{td_51gs_cliente:.2f}[s]\n"
                  f"Tap:{tap_51gs_cliente:.2f}\n"
                  f"Pickup:{pickup_51gs_cliente:.2f}[A]")
    ax.text(0.6, 2.5, txt_dt_cli, bbox=r_box, fontsize=8.5, color='red', va='top')
    ax.annotate('', xy=(pickup_51gs_cliente, 4), xytext=(5, 2.1), arrowprops=dict(arrowstyle='->', color='red'))

    txt_elec_cli = (f"Overcurrent Relay - Electronic (Neutro Cliente)\n"
                    f"SIEMENS 7SJ6X IEC I\n"
                    f"Tap Range:[0.25 / 12.0] Tap:{tap_neutro_cliente:.2f}\n"
                    f"Pickup:{pickup_neutro_cliente:.2f}[A] TD:{td_neutro_cliente}\n"
                    f"Inst. List (Pickup, Delay):({inst_prim_cliente:.1f}, 0.00)")
    ax.text(12, 0.45, txt_elec_cli, bbox=r_box, fontsize=8.5, color='red', va='top')
    ax.annotate('', xy=(pickup_neutro_cliente * 1.5, 0.35), xytext=(11, 0.35), arrowprops=dict(arrowstyle='->', color='red'))

    plt.figtext(0.5, 0.02, f"Figura A. Coordenograma de Neutro - CPFL x Cliente ({tensao} kV).", ha="center", fontsize=11)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    return 'data:image/png;base64,' + _fig_to_b64(fig)
