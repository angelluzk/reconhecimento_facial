# Importações necessárias para a manipulação de arquivos, datas e geração de relatórios.
import io # Para trabalhar com arquivos em memória (como PDF, Excel, etc.).
import pandas as pd # Para lidar com tabelas de dados (tipo Excel).
from datetime import datetime # Para mexer com datas e horas.

#Essas importações do reportlab são essenciais para criar e formatar o conteúdo dentro de um PDF de maneira personalizada e profissional. Elas ajudam a controlar desde o layout geral até os detalhes da formatação de tabelas, textos, cores, espaçamentos e até quebras de página.
from reportlab.lib.pagesizes import letter # Para gerar arquivos PDF do zero.
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors # Importa um módulo para definir cores dentro do PDF. Isso é útil para a personalização de elementos gráficos e de texto, como a cor de fundo de tabelas e texto.
from reportlab.lib.styles import getSampleStyleSheet # Essa função fornece um conjunto de estilos pré-definidos para formatação de texto no PDF (como o estilo "Title", "Heading1", "Normal", etc.).

from database.connection import get_db_connection

# Função para formatar uma data do banco (ex: 2025-04-18 14:30:00) para um formato mais legível (ex: 18/04/2025 14:30:00)
def formatar_data(data):
    try:
        # Tenta transformar a data de um formato padrão (banco de dados) para algo mais legível, tipo: 18/04/2025 14:00:00.
        return datetime.strptime(str(data), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        # Se der erro (tipo se o valor for nulo), retorna um tracinho ou o valor original.
        return str(data) if data else "—"

# Função para calcular o tempo total entre a entrada e saída.
def calcular_duracao(entrada_str, saida_str):
    try:
        # Converte as strings de hora para datetime, mas sem a data.
        entrada = datetime.strptime(entrada_str, "%H:%M:%S")
        saida = datetime.strptime(saida_str, "%H:%M:%S")

        # Calcula a diferença entre as duas horas.
        duracao = saida - entrada

        # Retorna a duração no formato adequado (horas:minutos:segundos).
        return str(duracao)
    except Exception:
        return "—"

# Função principal que consulta o banco e gera o relatório de presença com base nos filtros escolhidos.
def gerar_relatorio_presenca(data_inicio=None, data_fim=None, turno=None, turma=None, aluno=None, pagina=None, por_pagina=None):
    # Conecta no banco e cria um cursor que permite executar SQL.
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        filtros = []  # Lista onde vamos colocando os pedaços do WHERE da consulta.
        parametros = []  # Os valores que vão substituir os %s na query.

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

        where_clause = " AND ".join(filtros) if filtros else "1=1"  # se não tiver filtro, usa '1=1' só pra não quebrar a query.

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

        # Se não houver paginação, remove o LIMIT e OFFSET.
        if pagina is None or por_pagina is None:
            query = query.replace("LIMIT %s OFFSET %s", "")  # Remove LIMIT e OFFSET.

        # Aqui conta quantos resultados totais vão vir, pra saber quantas páginas precisa.
        if pagina is not None and por_pagina is not None:
            count_query = f"SELECT COUNT(*) as total FROM ({query}) AS sub"
            cursor.execute(count_query, parametros)
            total = cursor.fetchone()['total']
            total_paginas = max(1, (total + por_pagina - 1) // por_pagina)

            offset = (pagina - 1) * por_pagina
            query += " LIMIT %s OFFSET %s"
            parametros.extend([por_pagina, offset])
        else:
            total_paginas = 1  # Se não houver paginação, assume uma única página.

        cursor.execute(query, parametros)
        registros = cursor.fetchall()

        # Definindo o período integral das 8h00 às 17h00.
        periodo_integral_inicio = datetime.strptime("08:00:00", "%H:%M:%S")
        periodo_integral_fim = datetime.strptime("17:00:00", "%H:%M:%S")

        for reg in registros:
            # Formata data.
            if reg['data']:
                reg['data'] = datetime.strptime(str(reg['data']), "%Y-%m-%d").strftime("%d/%m/%Y")

            # Formata horários.
            entrada = reg['horario_entrada']
            saida = reg['horario_saida']
            if entrada:
                entrada_str = datetime.strptime(str(entrada), "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
                reg['horario_entrada'] = entrada_str
            else:
                reg['horario_entrada'] = "—"

            if saida:
                saida_str = datetime.strptime(str(saida), "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
                reg['horario_saida'] = saida_str
            else:
                reg['horario_saida'] = "—"

            # Cálculo da duração.
            if entrada and saida:
                entrada_dt = datetime.strptime(str(entrada), "%Y-%m-%d %H:%M:%S")
                saida_dt = datetime.strptime(str(saida), "%Y-%m-%d %H:%M:%S")
                duracao_timedelta = saida_dt - entrada_dt
                reg['duracao'] = str(duracao_timedelta)

                # Status com base no período integral.
                duracao_segundos = duracao_timedelta.total_seconds()
                periodo_integral_segundos = (periodo_integral_fim - periodo_integral_inicio).total_seconds()

                # Verifica se o aluno cumpriu o período integral.
                if duracao_segundos >= periodo_integral_segundos:
                    reg['status'] = "Presente"
                elif duracao_segundos > 0:
                    reg['status'] = "Presente parcial"
                else:
                    reg['status'] = "Incompleto"
            elif entrada and not saida:
                reg['duracao'] = "—"
                reg['status'] = "Incompleto"
            else:
                reg['duracao'] = "—"
                reg['status'] = "Faltou"

        conn.close()
        return registros, total_paginas

    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        conn.close()
        return [], 1

# Função que gera um PDF com os dados de presença organizados de forma simples e legível.
def gerar_pdf(registros, filtros=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elementos = []

    styles = getSampleStyleSheet()
    estilo_titulo = styles["Title"]
    estilo_subtitulo = styles["Normal"]

    # Título.
    elementos.append(Paragraph("Relatório de Presença", estilo_titulo))
    elementos.append(Spacer(1, 12))

    # Filtros aplicados.
    if filtros:
        filtros_formatados = []
        if filtros.get("data_inicio") and filtros.get("data_fim"):
            filtros_formatados.append(f"Período: {filtros['data_inicio']} a {filtros['data_fim']}")
        if filtros.get("turno"):
            filtros_formatados.append(f"Turno: {filtros['turno']}")
        if filtros.get("turma"):
            filtros_formatados.append(f"Turma: {filtros['turma']}")
        if filtros.get("aluno"):
            filtros_formatados.append(f"Aluno(a): {filtros['aluno']}")

        for f in filtros_formatados:
            elementos.append(Paragraph(f, estilo_subtitulo))
        elementos.append(Spacer(1, 12))

    # Cabeçalho da tabela.
    dados = [
        ["Aluno(a)", "Turma", "Turno", "Data", "Entrada", "Saída", "Duração", "Status"]
    ]

    # Corpo da tabela.
    for reg in registros:
        dados.append([
            reg['aluno'],
            reg['turma'],
            reg['turno'],
            reg['data'],
            reg['horario_entrada'],
            reg['horario_saida'],
            reg['duracao'],
            reg['status']
        ])

    # Tabela.
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

    # Rodapé com página e data.
    def rodape(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawString(30, 20, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas.drawRightString(580, 20, f"Página {doc.page}")
        canvas.restoreState()

    doc.build(elementos, onFirstPage=rodape, onLaterPages=rodape)

    buffer.seek(0)
    return buffer

# Função que gera uma planilha Excel (.xlsx) com os registros de presença.
def gerar_excel(registros, filtros=None):
    # Formata as datas de entrada e saída antes de criar o DataFrame.
    for reg in registros:
        reg['horario_entrada'] = formatar_data(reg['horario_entrada'])
        reg['horario_saida'] = formatar_data(reg['horario_saida'])

    df = pd.DataFrame(registros)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet('Presenças')
        writer.sheets['Presenças'] = worksheet

        row = 0

        # Escreve os filtros usados no topo.
        if filtros:
            if filtros.get("Data_inicio") and filtros.get("data_fim"):
                worksheet.write(row, 0, f"Período: {filtros['Data_inicio']} a {filtros['data_fim']}")
                row += 1
            if filtros.get("Turno"):
                worksheet.write(row, 0, f"Turno: {filtros['turno']}")
                row += 1
            if filtros.get("Turma"):
                worksheet.write(row, 0, f"Turma: {filtros['turma']}")
                row += 1
            if filtros.get("Aluno(a)"):
                worksheet.write(row, 0, f"Aluno(a): {filtros['aluno']}")
                row += 1
            row += 1  # espaço extra.

        # Escreve a tabela a partir da linha atual.
        df.to_excel(writer, sheet_name='Presenças', startrow=row, index=False)

    buffer.seek(0)
    return buffer

# Função que gera um arquivo de texto simples com os registros (sem formatação, só o conteúdo).
def gerar_txt(registros, filtros=None):
    buffer = io.StringIO()

    # Escreve filtros no topo.
    if filtros:
        if filtros.get("Data_inicio") and filtros.get("Data_fim"):
            buffer.write(f"Período: {filtros['data_inicio']} a {filtros['data_fim']}\n")
        if filtros.get("Turno"):
            buffer.write(f"Turno: {filtros['turno']}\n")
        if filtros.get("Turma"):
            buffer.write(f"Turma: {filtros['turma']}\n")
        if filtros.get("Aluno(a)"):
            buffer.write(f"Aluno(a): {filtros['aluno']}\n")
        buffer.write("\n")

    # Escreve os registros.
    for reg in registros:
        entrada_formatada = formatar_data(reg['horario_entrada'])
        saida_formatada = formatar_data(reg['horario_saida'])
        duracao = reg['duracao']
        status = reg['status']

        buffer.write(
            f"Aluno(a): {reg['aluno']} | Turma: {reg['turma']} | Turno: {reg['turno']} | "
            f"Entrada: {entrada_formatada} | Saída: {saida_formatada} | Duração: {duracao} | Status: {status}\n"
        )

    buffer.seek(0)
    return io.BytesIO(buffer.getvalue().encode('utf-8'))