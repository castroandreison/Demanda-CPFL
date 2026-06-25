-- GED-2855 Database Schema
-- Norma: Fornecimento de Energia Elétrica a Edifícios de Uso Coletivo

CREATE TABLE IF NOT EXISTS tabela10 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT,
    carga_min_kva REAL,
    carga_max_kva REAL,
    fator_demanda REAL
);

CREATE TABLE IF NOT EXISTS tabela11 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT,
    fator_demanda REAL
);

CREATE TABLE IF NOT EXISTS tabela12 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    carga_min_kva REAL,
    carga_max_kva REAL,
    fator_demanda REAL
);

CREATE TABLE IF NOT EXISTS tabela13 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    faixa TEXT,
    fator_demanda REAL
);

CREATE TABLE IF NOT EXISTS tabela14 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_carga TEXT,
    fator_demanda REAL
);

CREATE TABLE IF NOT EXISTS tabela15 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    demanda_kva REAL,
    trafo_kva REAL
);

CREATE TABLE IF NOT EXISTS tabela16 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_ligacao TEXT,
    demanda_min_kva REAL,
    demanda_max_kva REAL,
    categoria TEXT,
    disjuntor TEXT,
    condutor_cobre TEXT,
    condutor_aluminio TEXT,
    eletroduto TEXT,
    aterramento TEXT
);

CREATE TABLE IF NOT EXISTS tabela17 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fp_atual REAL,
    fp_desejado REAL,
    kvar_por_kw REAL
);

CREATE TABLE IF NOT EXISTS tabela20 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_edificacao TEXT,
    uso TEXT,
    demanda_unitaria_kva REAL
);

-- Seed data: Tabela 10 - Fatores de Demanda para Iluminação e Tomadas
INSERT OR IGNORE INTO tabela10 (descricao, carga_min_kva, carga_max_kva, fator_demanda) VALUES
('Iluminação e Tomadas - Residencial', 0, 3, 0.80),
('Iluminação e Tomadas - Residencial', 3.001, 5, 0.70),
('Iluminação e Tomadas - Residencial', 5.001, 10, 0.65),
('Iluminação e Tomadas - Residencial', 10.001, 999, 0.60),
('Iluminação e Tomadas - Comercial', 0, 5, 0.85),
('Iluminação e Tomadas - Comercial', 5.001, 10, 0.75),
('Iluminação e Tomadas - Comercial', 10.001, 20, 0.65),
('Iluminação e Tomadas - Comercial', 20.001, 999, 0.55),
('Iluminação e Tomadas - Industrial', 0, 10, 1.00),
('Iluminação e Tomadas - Industrial', 10.001, 999, 0.90);

-- Tabela 11 - Fatores de Demanda para Chuveiros e Aquecedores
INSERT OR IGNORE INTO tabela11 (descricao, fator_demanda) VALUES
('1 aparelho', 1.00),
('2 aparelhos', 0.75),
('3 aparelhos', 0.65),
('4 aparelhos', 0.60),
('5 aparelhos', 0.55),
('6 aparelhos', 0.50),
('7 aparelhos', 0.48),
('8 aparelhos', 0.46),
('9 aparelhos', 0.44),
('10 aparelhos', 0.42),
('11 ou mais', 0.40);

-- Tabela 12 - Fatores de Demanda para Eletrodomésticos
INSERT OR IGNORE INTO tabela12 (tipo, carga_min_kva, carga_max_kva, fator_demanda) VALUES
('Eletrodomésticos', 0, 3, 0.75),
('Eletrodomésticos', 3.001, 8, 0.60),
('Eletrodomésticos', 8.001, 999, 0.50);

-- Tabela 13 - Fatores de Demanda para Ar Condicionado
INSERT OR IGNORE INTO tabela13 (faixa, fator_demanda) VALUES
('1 a 10 aparelhos', 1.00),
('11 a 20 aparelhos', 0.90),
('21 a 30 aparelhos', 0.82),
('31 a 40 aparelhos', 0.80),
('41 a 50 aparelhos', 0.77),
('Acima de 50 aparelhos', 0.75);

-- Tabela 14 - Fatores de Demanda para Motores
INSERT OR IGNORE INTO tabela14 (tipo_carga, fator_demanda) VALUES
('1° maior motor', 1.00),
('2° maior motor', 0.90),
('3° ao 5° motor', 0.80),
('Demais motores', 0.70);

-- Tabela 15 - Transformadores Padrão (trafo_kva = tamanho nominal, demanda_kva = capacidade máxima)
INSERT OR IGNORE INTO tabela15 (demanda_kva, trafo_kva) VALUES
(15, 15),
(30, 30),
(45, 45),
(75, 75),
(112.5, 112.5),
(150, 150),
(225, 225),
(300, 300),
(500, 500),
(750, 750),
(1000, 1000),
(1500, 1500);

-- Tabela 16 - Padrão de Entrada
INSERT OR IGNORE INTO tabela16 (tipo_ligacao, demanda_min_kva, demanda_max_kva, categoria, disjuntor, condutor_cobre, condutor_aluminio, eletroduto, aterramento) VALUES
('Trifásico', 0, 15.9, 'C1', '30A', '6 mm²', '10 mm²', '25 mm', '6 mm²'),
('Trifásico', 16, 24.9, 'C2', '40A', '10 mm²', '16 mm²', '32 mm', '10 mm²'),
('Trifásico', 25, 35.9, 'C3', '60A', '16 mm²', '25 mm²', '40 mm', '16 mm²'),
('Trifásico', 36, 47.9, 'C4', '70A', '25 mm²', '35 mm²', '50 mm', '25 mm²'),
('Trifásico', 48, 62.9, 'C5', '80A', '35 mm²', '50 mm²', '60 mm', '35 mm²'),
('Trifásico', 63, 79.9, 'C6', '100A', '50 mm²', '70 mm²', '75 mm', '50 mm²'),
('Trifásico', 80, 99.9, 'C7', '125A', '70 mm²', '95 mm²', '75 mm', '70 mm²'),
('Trifásico', 100, 124.9, 'C8', '150A', '95 mm²', '120 mm²', '85 mm', '95 mm²'),
('Trifásico', 125, 149.9, 'C9', '175A', '120 mm²', '150 mm²', '85 mm', '120 mm²'),
('Trifásico', 150, 199.9, 'C10', '200A', '150 mm²', '185 mm²', '100 mm', '150 mm²'),
('Trifásico', 200, 249.9, 'C11', '250A', '185 mm²', '240 mm²', '100 mm', '185 mm²'),
('Trifásico', 250, 299.9, 'C12', '300A', '240 mm²', '300 mm²', '125 mm', '240 mm²'),
('Trifásico', 300, 399.9, 'C13', '400A', '2x120 mm²', '2x150 mm²', '125 mm', '2x120 mm²'),
('Trifásico', 400, 499.9, 'C14', '500A', '2x150 mm²', '2x185 mm²', '150 mm', '2x150 mm²'),
('Trifásico', 500, 599.9, 'C15', '600A', '2x185 mm²', '2x240 mm²', '150 mm', '2x185 mm²');

-- Tabela 17 - Fator de Correção de FP (kVAr por kW)
INSERT OR IGNORE INTO tabela17 (fp_atual, fp_desejado, kvar_por_kw) VALUES
(0.50, 0.92, 1.403),
(0.51, 0.92, 1.350),
(0.52, 0.92, 1.297),
(0.53, 0.92, 1.247),
(0.54, 0.92, 1.197),
(0.55, 0.92, 1.149),
(0.56, 0.92, 1.102),
(0.57, 0.92, 1.057),
(0.58, 0.92, 1.013),
(0.59, 0.92, 0.970),
(0.60, 0.92, 0.928),
(0.61, 0.92, 0.887),
(0.62, 0.92, 0.847),
(0.63, 0.92, 0.808),
(0.64, 0.92, 0.770),
(0.65, 0.92, 0.733),
(0.66, 0.92, 0.697),
(0.67, 0.92, 0.661),
(0.68, 0.92, 0.627),
(0.69, 0.92, 0.593),
(0.70, 0.92, 0.560),
(0.71, 0.92, 0.528),
(0.72, 0.92, 0.496),
(0.73, 0.92, 0.465),
(0.74, 0.92, 0.435),
(0.75, 0.92, 0.405),
(0.76, 0.92, 0.376),
(0.77, 0.92, 0.347),
(0.78, 0.92, 0.319),
(0.79, 0.92, 0.292),
(0.80, 0.92, 0.265),
(0.81, 0.92, 0.238),
(0.82, 0.92, 0.212),
(0.83, 0.92, 0.187),
(0.84, 0.92, 0.162),
(0.85, 0.92, 0.137),
(0.86, 0.92, 0.113),
(0.87, 0.92, 0.089),
(0.88, 0.92, 0.066),
(0.89, 0.92, 0.043),
(0.90, 0.92, 0.020),
(0.50, 0.95, 1.519),
(0.55, 0.95, 1.265),
(0.60, 0.95, 1.044),
(0.65, 0.95, 0.849),
(0.70, 0.95, 0.676),
(0.75, 0.95, 0.521),
(0.80, 0.95, 0.381),
(0.81, 0.95, 0.354),
(0.82, 0.95, 0.328),
(0.83, 0.95, 0.303),
(0.84, 0.95, 0.278),
(0.85, 0.95, 0.253),
(0.86, 0.95, 0.229),
(0.87, 0.95, 0.205),
(0.88, 0.95, 0.182),
(0.89, 0.95, 0.159),
(0.90, 0.95, 0.136),
(0.91, 0.95, 0.114),
(0.92, 0.95, 0.092);

-- Tabela 20 - Demanda Unitária por Tipo de Edificação
INSERT OR IGNORE INTO tabela20 (tipo_edificacao, uso, demanda_unitaria_kva) VALUES
('Residencial', 'Apartamento 1 dorm', 1.80),
('Residencial', 'Apartamento 2 dorm', 2.50),
('Residencial', 'Apartamento 3 dorm', 3.20),
('Residencial', 'Casa 1 dorm', 2.00),
('Residencial', 'Casa 2 dorm', 2.80),
('Residencial', 'Casa 3 dorm', 3.50),
('Comercial', 'Loja pequena', 3.00),
('Comercial', 'Loja média', 5.00),
('Comercial', 'Loja grande', 8.00),
('Comercial', 'Escritório pequeno', 2.50),
('Comercial', 'Escritório médio', 5.00),
('Comercial', 'Escritório grande', 10.00),
('Industrial', 'Pequeno porte', 10.00),
('Industrial', 'Médio porte', 25.00),
('Industrial', 'Grande porte', 50.00);
