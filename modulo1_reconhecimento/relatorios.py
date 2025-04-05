import io
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from database.connection import get_db_connection

def formatar_data(data):
    if data:
        try:
            return datetime.strptime(str(data), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
        except Exception:
            return str(data)
    return "—"

def calcular_duracao(entrada_str, saida_str):
    try:
        entrada = datetime.strptime(str(entrada_str), "%Y-%m-%d %H:%M:%S")
        saida = datetime.strptime(str(saida_str), "%Y-%m-%d %H:%M:%S")
        duracao = saida - entrada
        return str(duracao)
    except Exception:
        return "—"

def gerar_relatorio_presenca(data_inicio=None, data_fim=None, turno=None, turma=None, aluno=None):
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)
    filtros = []
    parametros = []

    if data_inicio and data_fim:
        filtros.append("DATE(r.data_hora) BETWEEN %s AND %s")
        parametros.extend([data_inicio, data_fim])
    if turno and turno not in ["", "Todos"]:
        filtros.append("a.turno = %s")
        parametros.append(turno)
    if turma:
        filtros.append("a.turma = %s")
        parametros.append(turma)
    if aluno:
        filtros.append("a.nome LIKE %s")
        parametros.append(f"%{aluno}%")

    where_clause = " AND ".join(filtros) if filtros else "1=1"

    query = f"""
        SELECT 
            a.nome AS aluno, 
            a.turma, 
            a.turno, 
            DATE(r.data_hora) AS data,
            MIN(CASE WHEN r.tipo_registro = 'entrada' THEN r.data_hora END) AS horario_entrada,
            MAX(CASE WHEN r.tipo_registro = 'saida' THEN r.data_hora END) AS horario_saida
        FROM registros_presenca r 
        JOIN alunos a ON r.id_aluno = a.id
        WHERE {where_clause}
        GROUP BY a.nome, a.turma, a.turno, DATE(r.data_hora)
        ORDER BY a.turma, a.nome, data
    """

    cursor.execute(query, tuple(parametros))
    registros = cursor.fetchall()
    cursor.close()
    conn.close()

    for reg in registros:
        entrada_raw = reg['horario_entrada']
        saida_raw = reg['horario_saida']

        reg['horario_entrada'] = formatar_data(entrada_raw)
        reg['horario_saida'] = formatar_data(saida_raw)
        reg['duracao'] = calcular_duracao(entrada_raw, saida_raw)

    return registros

def gerar_pdf(registros):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    largura, altura = letter

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(30, altura - 30, "Relatório de Presença")

    y = altura - 60
    pdf.setFont("Helvetica", 10)

    for reg in registros:
        texto = (
            f"Aluno: {reg['aluno']} | Turma: {reg['turma']} | Turno: {reg['turno']} | "
            f"Entrada: {reg['horario_entrada']} | Saída: {reg['horario_saida']} | Duração: {reg['duracao']}"
        )
        pdf.drawString(30, y, texto)
        y -= 20
        if y < 40:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = altura - 60

    pdf.save()
    buffer.seek(0)
    return buffer

def gerar_excel(registros):
    df = pd.DataFrame(registros)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, sheet_name='Presenças')
    buffer.seek(0)
    return buffer

def gerar_txt(registros):
    buffer = io.StringIO()
    for reg in registros:
        buffer.write(
            f"Aluno: {reg['aluno']} | Turma: {reg['turma']} | Turno: {reg['turno']} | "
            f"Entrada: {reg['horario_entrada']} | Saída: {reg['horario_saida']} | Duração: {reg['duracao']}\n"
        )
    buffer.seek(0)
    return io.BytesIO(buffer.getvalue().encode('utf-8'))
