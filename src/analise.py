import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import textwrap
import logging
from database import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Função para carregar os dados do banco de dados
def carregar_banco(db_name="Data/livraria.db"):
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

    total_antes = len(df)
    duplicados = df[df.duplicated(subset="titulo", keep=False)]
    if not duplicados.empty:
        print(f"Foram encontradas {len(duplicados)} linhas duplicadas!")
        print("Títulos que se repetem:")
        print(duplicados['titulo'].value_counts())
    else:
        print("\n✅ Nenhuma duplicata encontrada.")
    
    #  Limpeza de Preço para entrar apenas numeros e diminuir a chance de erro
    df_clean['preco'] = df_clean['preco'].str.replace(r'[^\d.]', '', regex=True).astype(float)

    #  padronizando o testo e removendo espaços em branco
    df_clean['disponibilidade'] = df_clean['disponibilidade'].str.strip()
    
    # 4. Remover duplicatas de títulos apenas se o preço forem identico, para nao remover livros de ediçoes diferentes
    df_clean = df_clean.drop_duplicates(subset="titulo")
    
    return df_clean   

def gerar_tabela_visual(df):
    
    # coloquei apenas os 20 primeiros para visualizar melhor 
    df_top = df[['id','titulo', 'preco', 'disponibilidade','categoria','avaliacao']].head(20)
    #evitar que o titulo ultrapasse a tabela e fique muito grande
    df_top['titulo'] = df_top['titulo'].apply(lambda x: str(x)[:28] + '...' if len(str(x)) > 28 else str(x))
    # Criei uma figura específica para a tabela
    fig, ax = plt.subplots(figsize=(16, 7))
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

    plt.title("Resumo de Livros Coletados (Top 20)", fontsize=14, pad=20)
    plt.show()

def analisar_disponibilidade(df):
    # 1. Contagem baseada no texto para descobrir quantos livros estão em estoque e quantos estão esgotados
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
    plt.show() 

def gerar_tabela_categorias(df):
    """
    Gera uma tabela visual mostrando as 15 categorias com mais livros.
    """
    # contando a quantidade de livros por categoria e ordenando elas do maior para o menor
    df_cat = df['categoria'].value_counts().reset_index()
    df_cat.columns = ['Categoria', 'Qtd de Livros']
    df_cat_top = df_cat.head(15) 

    # 2. Configurando a figura
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis('off') # Esconde os eixos numéricos

    # 3. Desenhando a tabela
    tabela_cat = ax.table(
        cellText=df_cat_top.values,
        colLabels=df_cat_top.columns,
        cellLoc='center',
        loc='center'
    )
    
    # 4. Estilizando
    tabela_cat.auto_set_font_size(False)
    tabela_cat.set_fontsize(10)
    tabela_cat.scale(1.2, 1.5)
    tabela_cat.auto_set_column_width(col=list(range(len(df_cat_top.columns))))
    
    plt.title("Top 15 Categorias com Mais Livros", fontsize=14, pad=20)
    plt.tight_layout()
    plt.show()


def gerar_tabela_estrelas(df):
    """
    Gera uma tabela visual mostrando a quantidade de livros por avaliação (1 a 5 estrelas).
    """
    # contando a quantidade de livros por avaliação e ordenando do maior para o menor,pois os dados estao entrando nessa ordem
    df_aval = df['avaliacao'].value_counts().sort_index(ascending=False).reset_index()
    df_aval.columns = ['Estrelas', 'Qtd de Livros']
    df_aval['Estrelas'] = df_aval['Estrelas'].apply(lambda x: f"{int(x)} Estrela(s)")

    # 2. Configurando a figura para a tabela de avaliações
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axis('off')

    # 3. Desenhando a tabela
    tabela_aval = ax.table(
        cellText=df_aval.values,
        colLabels=df_aval.columns,
        cellLoc='center',
        loc='center'
    )
    
    # 4. Estilizando
    tabela_aval.auto_set_font_size(False)
    tabela_aval.set_fontsize(11)
    tabela_aval.scale(1.2, 1.8) 
    tabela_aval.auto_set_column_width(col=list(range(len(df_aval.columns))))
    
    plt.title("Quantidade de Livros por Avaliação", fontsize=14, pad=20)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
   
   df_raw = carregar_banco("Data/livraria.db")
    
   if df_raw is not None and not df_raw.empty:
        df_final = limpar_dados(df_raw)
        
        # Passo 3: Mostra resultados e Gráficos
        print(df_final[['titulo', 'preco', 'disponibilidade','categoria','avaliacao']].head())
        analisar_disponibilidade(df_final)
        gerar_tabela_visual(df_final)
        gerar_tabela_categorias(df_final)
        gerar_tabela_estrelas(df_final)
   else:
        logging.warning("O banco de dados está vazio ou não foi encontrado.")