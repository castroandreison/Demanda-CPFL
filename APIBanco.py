import sqlite3
import pandas as pd
from pathlib import Path


class GED119API:

    def __init__(self, db_path="database/ged119_all_tables.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row


    # ----------------------------
    # UTILIDADES
    # ----------------------------

    def list_tables(self):
        """Lista todas as tabelas do banco"""
        query = """
        SELECT name FROM sqlite_master
        WHERE type='table'
        """
        return pd.read_sql(query, self.conn)


    def table_to_dataframe(self, table):
        """Retorna tabela inteira"""
        query = f"SELECT * FROM {table}"
        return pd.read_sql(query, self.conn)


    # ----------------------------
    # FATOR DEMANDA ILUMINAÇÃO
    # ----------------------------

    def get_fator_demanda_iluminacao(self, tipo):
        query = """
        SELECT *
        FROM fator_demanda_iluminacao
        WHERE descricao LIKE ?
        """
        return pd.read_sql(query, self.conn, params=(f"%{tipo}%",))


    # ----------------------------
    # FATOR DEMANDA APARELHOS
    # ----------------------------

    def get_fator_demanda_aparelhos(self, quantidade):

        query = """
        SELECT fator_demanda
        FROM fator_demanda_aparelhos
        WHERE quantidade_min <= ?
        AND quantidade_max >= ?
        """

        df = pd.read_sql(query, self.conn, params=(quantidade, quantidade))

        if not df.empty:
            return df.iloc[0]["fator_demanda"]

        return None


    # ----------------------------
    # POTÊNCIA APARELHOS
    # ----------------------------

    def get_potencia_aparelho(self, nome):

        query = """
        SELECT potencia_kw
        FROM potencia_minima_aparelhos
        WHERE equipamento LIKE ?
        """

        df = pd.read_sql(query, self.conn, params=(f"%{nome}%",))

        if not df.empty:
            return df.iloc[0]["potencia_kw"]

        return None


    # ----------------------------
    # MOTORES
    # ----------------------------

    def get_motor_por_hp(self, hp):

        query = """
        SELECT *
        FROM motores_potencia
        WHERE potencia_hp = ?
        """

        return pd.read_sql(query, self.conn, params=(hp,))


    # ----------------------------
    # SIMULTANEIDADE APARTAMENTOS
    # ----------------------------

    def get_coeficiente_apartamentos(self, qtd):

        query = """
        SELECT coeficiente
        FROM coeficiente_simultaneidade
        WHERE aptos_min <= ?
        AND aptos_max >= ?
        """

        df = pd.read_sql(query, self.conn, params=(qtd, qtd))

        if not df.empty:
            return df.iloc[0]["coeficiente"]

        return None


    # ----------------------------
    # CAPACIDADE CABOS
    # ----------------------------

    def get_capacidade_cabo(self, secao):

        query = """
        SELECT *
        FROM capacidade_cabos_bt
        WHERE secao_mm2 = ?
        """

        return pd.read_sql(query, self.conn, params=(secao,))


    # ----------------------------
    # TRANSFORMADORES
    # ----------------------------

    def get_transformador(self, kva):

        query = """
        SELECT *
        FROM transformadores
        WHERE potencia_kva = ?
        """

        return pd.read_sql(query, self.conn, params=(kva,))


    # ----------------------------
    # CONSULTA GENÉRICA
    # ----------------------------

    def query(self, sql, params=None):

        return pd.read_sql(sql, self.conn, params=params)


    # ----------------------------
    # FECHAR CONEXÃO
    # ----------------------------

    def close(self):
        self.conn.close()