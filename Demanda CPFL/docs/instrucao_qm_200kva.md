## INSTRUÇÃO: DIMENSIONAMENTO DE QUADROS DE MEDIDORES (GED-119 item 13.3)

### Regra (literal):
> "O quadro de medidores deve ser constituído de um ou mais quadros, justapostos ou não, contendo, cada um, o máximo de 36 medidores e demanda calculada de no máximo 200 kVA."

### Lógica do seletor:

1. Entradas:
   - `numero_apartamentos` (N)
   - `demanda_total_kva` (Dg)
   - `incluir_adm` (bool, padrao True)

2. Calcular:
   - `medidores = N + (1 se incluir_adm else 0)`
   - `qms_min_por_medidores = ceil(medidores / 36)`
   - `qms_min_por_demanda = ceil(Dg / 200)`
   - **`qms_necessarios = max(qms_min_por_medidores, qms_min_por_demanda)`**

3. Distribuir medidores entre os QMs:
   - Cada QM recebe no máximo 36 medidores
   - Distribuir uniformemente (ou manter adm no último QM)
   - Cada QM respeita: `demanda_por_qm = Dg / qms_necessarios ≤ 200`

4. Se `qms_necessarios > qms_min_por_medidores`:
   - **Alerta:** "Demanda total supera 200 kVA por QM. Necessário aumentar número de QMs."
   - **Solução:** distribuir os `medidores` em `qms_necessarios` QMs

### Exemplos:

| Caso | Aptos | Adm | Medidores | Dg (kVA) | QMs por med | QMs por demanda | QMs total | Distribuição |
|---|---|---|---|---|---|---|---|---|
| Ed. Maestro | 35 | sim | 36 | 294,47 | ceil(36/36)=1 | ceil(294,47/200)=2 | **2** | 18+18 |
| Pequeno | 12 | sim | 13 | 80 | ceil(13/36)=1 | ceil(80/200)=1 | **1** | 13 |
| Grande | 81 | sim | 82 | 294,47 | ceil(82/36)=3 | ceil(294,47/200)=2 | **3** | 36+36+10 |
| 120 aptos | 120 | sim | 121 | 500 | ceil(121/36)=4 | ceil(500/200)=3 | **4** | 36+36+36+13 |

### Regra de ouro:
- **Sempre** pegar o maior entre os dois critérios (medidores e demanda)
- Se demanda for o fator determinante, redistribuir os medidores para caber nos QMs adicionais
- O material (metal/policarbonato) **não** é definido pela demanda

### Saída esperada no relatório:
- Critério 1 (medidores): X QMs
- Critério 2 (demanda): Y QMs
- QMs necessários: max(X, Y)
- Se Y > X: alerta amarelo "Demanda supera 200 kVA/QM"
- Se X === Y: indicação verde "Ambos os critérios convergem"
- Cada QM listado com medidores, dimensões e demanda individual
