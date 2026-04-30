import sqlite3
import logging
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    def __init__(self, db_name: str = "Data/livraria.db"):
        self.db_name = db_name

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def update_books_info(self, df: pd.DataFrame):
        """
        Atualiza a categoria e a avaliação de livros que já existem no banco,
        usando o título como chave de busca.
        """
        query = """
            UPDATE livros 
            SET categoria = ?, avaliacao = ? 
            WHERE titulo = ?
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Prepara os dados para o update (categoria, avaliacao, titulo)
                # A ordem aqui deve ser a mesma das '?' na query acima
                dados = df[['categoria', 'avaliacao', 'titulo']].values.tolist()
                
                cursor.executemany(query, dados)
                conn.commit()
                logging.info(f"Dados de {cursor.rowcount} livros foram atualizados com sucesso!")
        except Exception as e:
            logging.error(f"Erro ao atualizar o banco: {e}")

class BooksScraper:
    BASE_URL = "https://books.toscrape.com/"
    ESTRELAS_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    def __init__(self):
        self.session = requests.Session()

    def get_categories(self) -> dict:
        response = self.session.get(self.BASE_URL)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.select('.side_categories > ul > li > ul > li > a')
        return {link.text.strip(): urljoin(self.BASE_URL, link['href']) for link in links}

    def scrape_for_update(self):
        categories = self.get_categories()
        all_books_data = []

        for category_name, url in categories.items():
            logging.info(f"Lendo categoria: {category_name}")
            current_url = url
            
            while True:
                response = self.session.get(current_url)
                soup = BeautifulSoup(response.content, 'html.parser')
                books = soup.select('article.product_pod')

                for book in books:
                    titulo = book.h3.a['title']
                    classe_estrela = book.select_one('.star-rating')['class'][1]
                    avaliacao = self.ESTRELAS_MAP.get(classe_estrela, 0)

                    all_books_data.append({
                        'titulo': titulo,
                        'categoria': category_name,
                        'avaliacao': avaliacao
                    })

                next_btn = soup.select_one('li.next > a')
                if next_btn:
                    current_url = urljoin(current_url, next_btn['href'])
                else:
                    break

        return pd.DataFrame(all_books_data)

# --- Execução do Incremento ---
if __name__ == "__main__":
    db = DatabaseManager()
    scraper = BooksScraper()
    
    # 1. Coleta apenas Título, Categoria e Estrelas do site
    logging.info("Iniciando coleta de dados para atualização...")
    df_novos_dados = scraper.scrape_for_update()

    # 2. Atualiza os registros existentes no seu banco
    if not df_novos_dados.empty:
        db.update_books_info(df_novos_dados)
    else:
        logging.warning("Nenhum dado coletado para atualizar.")