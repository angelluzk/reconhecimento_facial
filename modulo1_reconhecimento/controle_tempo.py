# Este módulo é responsável por lidar com a configuração de tempo de espera entre registros de entrada e saída dos alunos. Ele acessa o banco de dados para buscar e atualizar essa informação conforme definido pelo administrador do sistema.

from database.connection import get_db_connection # Importa a função que conecta ao banco de dados.

# Função que busca a configuração atual do tempo de espera no banco de dados.
def obter_configuracao_tempo():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) # Cria um cursor com retorno em formato de dicionário (chave: nome da coluna).
    cursor.execute("SELECT * FROM configuracoes WHERE nome_configuracao = 'tempo_espera'") # Executa a consulta SQL para buscar a configuração com nome 'tempo_espera'.
    configuracao = cursor.fetchone()
    cursor.close()
    conn.close()
    return configuracao

# Função que atualiza o valor e o tipo (ex: minutos, horas) do tempo de espera no banco de dados.
def atualizar_configuracao_tempo(valor, tipo):
    conn = get_db_connection()
    cursor = conn.cursor() # Cria um cursor padrão (sem formato de dicionário aqui porque é apenas update).

    # Executa a atualização no banco de dados para o campo 'tempo_espera'.
    cursor.execute("""
        UPDATE configuracoes
        SET valor = %s, tipo = %s
        WHERE nome_configuracao = 'tempo_espera'
    """, (valor, tipo)) # Os valores %s são preenchidos com segurança pelos parâmetros.
    conn.commit()
    cursor.close()
    conn.close()