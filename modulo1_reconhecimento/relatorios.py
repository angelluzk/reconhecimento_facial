from datetime import datetime
from database.connection import get_db_connection

def gerar_relatorio_presenca(data_inicio, data_fim):

    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT a.nome AS aluno, r.tipo_registro, r.data_hora
        FROM registros_presenca r
        JOIN alunos a ON r.id_aluno = a.id
        WHERE DATE(r.data_hora) BETWEEN %s AND %s
        ORDER BY r.data_hora ASC
    """
    
    cursor.execute(query, (data_inicio, data_fim))
    registros = cursor.fetchall()
    
    conn.close()
    return registros