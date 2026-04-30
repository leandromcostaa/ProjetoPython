import sqlite3
import logging
import pandas as pd
from typing import List, Dict

class DatabaseManager:
    #iniciando o banco de dados, criando uma tabela se não existir
    def __init__(self,db_name: str = "livraria.db"):
        self.db_name = db_name
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

#criando a tabela de livros com os campos necessários
    def _create_table(self):
         query = """
         CREATE TABLE IF NOT EXISTS livros(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         titulo TEXT NOT NULL,
         preco REAL,
         disponibilidade TEXT,
         data_extracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
         );
"""
         with self._get_connection() as conn:
              conn.execute(query)
              logging.info("Tabela 'livros' verificada com sucesso!")

#função para inserir os dados dos livros coletados no banco de dados
    def insert_books(self, df: pd.DataFrame):
       
         try:
              with self._get_connection() as conn:
                   df.to_sql('livros', conn, if_exists='append', index=False)
                   logging.info(f"{len(df)} livros inseridos no banco com sucesso!")
         except Exception as e:
              logging.error(f"erro ao inserir no banco: {e}")