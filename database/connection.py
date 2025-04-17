# Este arquivo é responsável por conectar o sistema ao banco de dados MySQL.

import mysql.connector
import os # Importando o os para acessar variáveis de ambiente (como usuário e senha do banco).
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis de ambiente do arquivo .env para o ambiente do Python. Isso permite que a gente esconda informações sensíveis, como a senha do banco.

# Função que cria e retorna a conexão com o banco de dados.
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        conn.autocommit = True # Define que todas as alterações no banco devem ser salvas automaticamente.
        return conn # Se tudo deu certo, retorna a conexão para ser usada em outras partes do código.
    
    # Caso ocorra algum erro (como dados errados ou banco offline), ele mostra uma mensagem no terminal.
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None # Retorna None caso não consiga conectar.