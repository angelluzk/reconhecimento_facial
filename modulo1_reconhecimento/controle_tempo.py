from database.connection import get_db_connection

def obter_configuracao_tempo():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM configuracoes WHERE nome_configuracao = 'tempo_espera'")
    configuracao = cursor.fetchone()
    cursor.close()
    conn.close()
    return configuracao

def atualizar_configuracao_tempo(valor, tipo):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE configuracoes
        SET valor = %s, tipo = %s
        WHERE nome_configuracao = 'tempo_espera'
    """, (valor, tipo))
    conn.commit()
    cursor.close()
    conn.close()