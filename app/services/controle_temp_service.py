from app.database.connection import get_db_connection

def obter_configuracao_tempo():
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT * FROM configuracoes WHERE nome_configuracao = 'tempo_espera'")
                configuracao = cursor.fetchone()
        return configuracao
    except Exception as e:
        print(f"❌ Erro ao obter configuração de tempo: {e}")
        return None


def atualizar_configuracao_tempo(valor, tipo):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE configuracoes
                    SET valor = %s, tipo = %s
                    WHERE nome_configuracao = 'tempo_espera'
                """, (valor, tipo))
                conn.commit()
    except Exception as e:
        print(f"❌ Erro ao atualizar configuração de tempo: {e}")
        raise