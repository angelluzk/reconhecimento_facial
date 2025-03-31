# Módulo responsável pela conexão com o banco de dados MySQL.
import pymysql
import os
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

# Função para estabelecer e retornar uma conexão com o banco de dados.
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "reconhecimento_facial"),
        cursorclass=pymysql.cursors.DictCursor
    )
