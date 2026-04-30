import logging
from typing import List, Dict, Optional
from selenium import webdriver 
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
from database import DatabaseManager
import matplotlib.pyplot as plt

#configurando o logging para melhor monitoramento do processo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class bookscraper:
    #inicializando o scraper, configurando o driver e a URL alvo
    def __init__(self, headless:bool = True):
        self.url = "https://books.toscrape.com/"
        self.driver = self._setup_driver(headless)
        self.wait = WebDriverWait(self.driver, 10)

#configurando o driver do firefox, com opção de headless e algumas preferências para otimizar a raspagem
    def _setup_driver(self, headless: bool) -> webdriver.firefox:
            options = webdriver.FirefoxOptions()
            if headless:
                options.add_argument("--headless")
                options.set_preference("dom.webnotifications.enabled", False)
                options.set_preference("permissions.default.image", 2)
            return webdriver.Firefox(options=options)


#função para extrair os dados de cada livro na página
    def pegar_todos_livros(self) -> List[dict]:

       lista_de_livros=[]
       biblioteca = self.driver.find_elements(By.CLASS_NAME, "product_pod")

       for livro in biblioteca:
         try:
          titulo = livro.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a").get_attribute("title")
          preco = livro.find_element(By.CSS_SELECTOR, "p.price_color").text
          disponibilidade = livro.find_element(By.CSS_SELECTOR, "p.availability").text.strip()

          lista_de_livros.append({
              "titulo": titulo,
              "preco": preco,
              "disponibilidade": disponibilidade
         })
        
 
         except Exception as e:
              logging.warning(f"falha ao extrair arquivos: {e}")
              continue
       return lista_de_livros
 
 #função para controlar o fluxo de raspagem, coletando os dados dos livros
    def run(self) -> List[dict]:
      todos_livros = []
      paginas = 1
      
      try:
         self.driver.get(self.url)
         while True:
            logging.info(f"raspando a pagina: {paginas}...")

            self.wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME,"product_pod")))
            dado_pagina = self.pegar_todos_livros()
            todos_livros.extend(dado_pagina)

            try:
                prox_btn =  self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next a")))
                self.driver.execute_script("arguments[0].scrollIntoView();", prox_btn)
                self.driver.execute_script("arguments[0].click();", prox_btn)
                paginas += 1
                sleep(0.1)                
            except TimeoutException:
                logging.info("chegamos a ultima página.")
                break

      except TimeoutException:
        logging.error("Timeout: o site demorou muito para responder.")
      except Exception as e:
        logging.error(f"erro inesperado: {e}")
      finally:
        self.driver.quit()
        logging.info(f"processo finalizado,o total de livros foi:{len(todos_livros)}")  
      return todos_livros
   
        
if __name__ == "__main__":
    scraper = bookscraper(headless=True)
    dados = scraper.run()
    if dados:
       df = pd.DataFrame(dados)
       db = DatabaseManager()
       db.insert_books(df)