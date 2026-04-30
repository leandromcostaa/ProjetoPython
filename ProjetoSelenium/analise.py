import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import logging
from database import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

#função para limpar o preço, removendo símbolos e convertendo para float
def carregar_banco(db_name="livraria.db"):
    try:
      conn = sqlite3.connect(db_name)
      query = "SELECT * FROM livros"
      df = pd.read_sql_query(query, conn)
      conn.close()
      return df
    except Exception as e:
      logging.error(f"Erro ao ler o banco de dados: {e}")
      return None

def limpar_dados(df):
    """Transforma textos brutos em números para os gráficos."""
    logging.info("Limpando dados para o dashboard...")
    
    df_clean = df.copy()

    #  Limpeza de Preço para entrar apenas numeros
    df_clean['preco'] = df_clean['preco'].str.replace(r'[^\d.]', '', regex=True).astype(float)

    #  padronizando o testo e removendo espaços em branco
    df_clean['disponibilidade'] = df_clean['disponibilidade'].str.strip()
    
    # 4. Remover duplicatas de títulos
    df_clean = df_clean.drop_duplicates(subset=["titulo", "preco"])
    
    return df_clean   

def gerar_tabela_visual(df):
    # coloquei apenas os 10 primeiros para visualizar melhor
    df_top = df[['titulo', 'preco', 'disponibilidade']].head(10)
    
    # Criei uma figura específica para a tabela
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('off')  # Esconde os eixos do gráfico (X e Y)

    # Criando a tabela
    tabela = ax.table(
        cellText=df_top.values, 
        colLabels=df_top.columns, 
        cellLoc='center', 
        loc='center'
    )

    # Estilizando a tabela
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    tabela.scale(1.2, 1.5) # Ajusta o tamanho das células

    plt.title("Resumo de Livros Coletados (Top 10)", fontsize=14, pad=20)
    plt.show()

def analisar_disponibilidade(df):
    # 1. Contagem baseada no texto
    disponiveis = df[df['disponibilidade'].str.contains('In stock', case=False, na=False)].shape[0]
    esgotados = df[df['disponibilidade'].str.contains('Esgotado', case=False, na=False)].shape[0]

    # 2. Dados para o gráfico
    labels = ['Em Estoque', 'Esgotados']
    valores = [disponiveis, esgotados]
    cores = ['#2ecc71', '#e74c3c']

    # 3. Criando a figura e o gráfico (Apenas UMA vez)
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.pie(
        valores, 
        labels=labels, 
        autopct=lambda p: f'{p:.1f}%\n({int(p*sum(valores)/100)} und)', # Mostra % e qtd real
        startangle=90, 
        colors=cores,
        explode=(0.05, 0), 
        shadow=True
    )

    plt.title(f"Status do Inventário - Total: {len(df)} livros")
    
    # Adicionando uma legenda lateral para ficar profissional
    ax.legend(labels, title="Status", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    plt.tight_layout()
    plt.show() # Este comando abre a janela e pausa a execução até você fechar

    # Relatório impresso no terminal
    print(f"\n--- Relatório de Estoque ---")
    print(f"Disponíveis: {disponiveis}")
    print(f"Esgotados: {esgotados}")

if __name__ == "__main__":
   
   df_raw = carregar_banco("livraria.db")
    
   if df_raw is not None and not df_raw.empty:
        # Passo 2: Limpa os dados (Regex e Conversão)
        df_final = limpar_dados(df_raw)
        
        # Passo 3: Mostra resultados e Gráficos
        print(df_final[['titulo', 'preco', 'disponibilidade']].head())
        analisar_disponibilidade(df_final)
        gerar_tabela_visual(df_final)
   else:
        logging.warning("O banco de dados está vazio ou não foi encontrado.")