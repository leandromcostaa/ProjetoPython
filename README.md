# ProjetoPython
1. Crie uma biblioteca virtual .venv
2. ative a biblioteca com .venv\scripts\activate
3. baixe o requirements txt com pip install -r requirements.txt
# Ordem de carregamento
1. Rode o arquivo scrapy.py para puxar os primeiros dados e popular o banco
2. rode o arquivo scrapy2.py para dar update na tabela com novas informações
3. rode o arquivo analise.py para gerar os dashboard
# Estutura do Banco de dados
Coluna,Tipo,Descrição

id,INTEGER,Chave primária autoincremento

titulo,TEXT,Título completo do livro

preco,REAL,Preço do livro (opcional)

disponibilidade,TEXT,Status de estoque (opcional)

categoria,TEXT,Categoria extraída da barra lateral

avaliacao,REAL,Nota do livro convertida para numeral (1-5)

data_extracao,TIMESTAMP,Data e hora da coleta

