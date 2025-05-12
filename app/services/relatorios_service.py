import io
import pandas as pd
from datetime import datetime
from io import BytesIO, StringIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from app.database.connection import get_db_connection


def formatar_data(data):
    try:
        return datetime.strptime(str(data), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return str(data) if data else "—"


def calcular_duracao(entrada_str, saida_str):
    try:
        entrada = datetime.strptime(entrada_str, "%H:%M:%S")
        saida = datetime.strptime(saida_str, "%H:%M:%S")

        duracao = saida - entrada

        return str(duracao)
    except Exception:
        return "—"


def gerar_relatorio_presenca(data_inicio=None, data_fim=None, turno=None, turma=None, aluno=None, pagina=None, por_pagina=None):

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
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

        if pagina is None or por_pagina is None:
            query = query.replace("LIMIT %s OFFSET %s", "")

        if pagina is not None and por_pagina is not None:
            count_query = f"SELECT COUNT(*) as total FROM ({query}) AS sub"
            cursor.execute(count_query, parametros)
            total = cursor.fetchone()['total']
            total_paginas = max(1, (total + por_pagina - 1) // por_pagina)

            offset = (pagina - 1) * por_pagina
            query += " LIMIT %s OFFSET %s"
            parametros.extend([por_pagina, offset])
        else:
            total_paginas = 1

        cursor.execute(query, parametros)
        registros = cursor.fetchall()

        periodo_integral_inicio = datetime.strptime("08:00:00", "%H:%M:%S")
        periodo_integral_fim = datetime.strptime("17:00:00", "%H:%M:%S")

        for registro in registros:
            if registro['data']:
                registro['data'] = datetime.strptime(
                    str(registro['data']), "%Y-%m-%d").strftime("%d/%m/%Y")

            entrada = registro['horario_entrada']
            saida = registro['horario_saida']
            if entrada:
                entrada_str = datetime.strptime(
                    str(entrada), "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
                registro['horario_entrada'] = entrada_str
            else:
                registro['horario_entrada'] = "—"

            if saida:
                saida_str = datetime.strptime(
                    str(saida), "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
                registro['horario_saida'] = saida_str
            else:
                registro['horario_saida'] = "—"

            if entrada and saida:
                entrada_dt = datetime.strptime(
                    str(entrada), "%Y-%m-%d %H:%M:%S")
                saida_dt = datetime.strptime(str(saida), "%Y-%m-%d %H:%M:%S")
                duracao_timedelta = saida_dt - entrada_dt
                registro['duracao'] = str(duracao_timedelta)

                duracao_segundos = duracao_timedelta.total_seconds()
                periodo_integral_segundos = (
                    periodo_integral_fim - periodo_integral_inicio).total_seconds()

                if duracao_segundos >= periodo_integral_segundos:
                    registro['status'] = "Presente"
                elif duracao_segundos > 0:
                    registro['status'] = "Presente parcial"
                else:
                    registro['status'] = "Incompleto"
            elif entrada and not saida:
                registro['duracao'] = "—"
                registro['status'] = "Incompleto"
            else:
                registro['duracao'] = "—"
                registro['status'] = "Faltou"

        return registros, total_paginas

    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        return [], 1

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def gerar_pdf(registros, filtros=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elementos = []

    styles = getSampleStyleSheet()
    estilo_titulo = styles["Title"]
    estilo_subtitulo = styles["Normal"]

    elementos.append(Paragraph("Relatório de Presença", estilo_titulo))
    elementos.append(Spacer(1, 12))

    if filtros:
        filtros_formatados = []
        if filtros.get("data_inicio") and filtros.get("data_fim"):
            filtros_formatados.append(
                f"Período: {filtros['data_inicio']} a {filtros['data_fim']}")
        if filtros.get("turno") and filtros['turno'] != 'Todos':
            filtros_formatados.append(f"Turno: {filtros['turno']}")
        if filtros.get("turma"):
            filtros_formatados.append(f"Turma: {filtros['turma']}")
        if filtros.get("aluno"):
            filtros_formatados.append(f"Aluno: {filtros['aluno']}")

        for f in filtros_formatados:
            elementos.append(Paragraph(f, estilo_subtitulo))
        elementos.append(Spacer(1, 12))

    dados = [["Aluno", "Turma", "Turno", "Data",
              "Entrada", "Saída", "Duração", "Status"]]

    for reg in registros:
        dados.append([reg['aluno'], reg['turma'], reg['turno'], reg['data'],
                     reg['horario_entrada'], reg['horario_saida'], reg['duracao'], reg['status']])

    tabela = Table(dados, repeatRows=1)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elementos.append(tabela)

    def rodape(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawString(
            30, 20, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas.drawRightString(580, 20, f"Página {doc.page}")
        canvas.restoreState()

    doc.build(elementos, onFirstPage=rodape, onLaterPages=rodape)

    buffer.seek(0)
    return buffer


def gerar_excel(registros, filtros=None):
    for reg in registros:
        reg['horario_entrada'] = formatar_data(reg['horario_entrada'])
        reg['horario_saida'] = formatar_data(reg['horario_saida'])

    df = pd.DataFrame(registros)

    buffer = BytesIO()
    try:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('Presenças')
            writer.sheets['Presenças'] = worksheet

            row = 0

            if filtros:
                if filtros.get("data_inicio") and filtros.get("data_fim"):
                    worksheet.write(
                        row, 0, f"Período: {filtros['data_inicio']} a {filtros['data_fim']}")
                    row += 1
                if filtros.get("turno") and filtros['turno'] != 'Todos':
                    worksheet.write(row, 0, f"Turno: {filtros['turno']}")
                    row += 1
                if filtros.get("turma"):
                    worksheet.write(row, 0, f"Turma: {filtros['turma']}")
                    row += 1
                if filtros.get("aluno"):
                    worksheet.write(row, 0, f"Aluno: {filtros['aluno']}")
                    row += 1
                row += 1

            header_format = workbook.add_format(
                {'bold': True, 'bg_color': '#f9f9f9', 'border': 1, 'align': 'center'})
            for col_num, col_name in enumerate(df.columns):
                worksheet.write(0, col_num, col_name, header_format)

            for row_num, row_data in df.iterrows():
                for col_num, value in enumerate(row_data):
                    worksheet.write(row_num + 1, col_num, value)

            for col_num in range(len(df.columns)):
                worksheet.set_column(col_num, col_num, max(df[df.columns[col_num]].astype(
                    str).apply(len).max(), len(df.columns[col_num])) + 2)

        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"❌ Erro ao gerar Excel: {e}")
        return None


def gerar_txt(registros, filtros=None):
    buffer = StringIO()

    if filtros:
        if filtros.get("data_inicio") and filtros.get("data_fim"):
            buffer.write(
                f"Período: {filtros['data_inicio']} a {filtros['data_fim']}\n")
        if filtros.get("turno") and filtros['turno'] != 'Todos':
            buffer.write(f"Turno: {filtros['turno']}\n")
        if filtros.get("turma"):
            buffer.write(f"Turma: {filtros['turma']}\n")
        if filtros.get("aluno"):
            buffer.write(f"Aluno: {filtros['aluno']}\n")
        buffer.write("\n")

    for reg in registros:
        entrada_formatada = formatar_data(reg['horario_entrada'])
        saida_formatada = formatar_data(reg['horario_saida'])
        duracao = reg['duracao']
        status = reg['status']

        buffer.write(
            f"Aluno: {reg['aluno']} | Turma: {reg['turma']} | Turno: {reg['turno']} | "
            f"Entrada: {entrada_formatada} | Saída: {saida_formatada} | Duração: {duracao} | Status: {status}\n"
        )

    buffer.seek(0)
    return io.BytesIO(buffer.getvalue().encode('utf-8'))