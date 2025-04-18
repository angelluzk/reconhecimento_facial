# Importações necessárias para a manipulação de arquivos, datas e geração de relatórios.
import io # Para trabalhar com arquivos em memória (como PDF, Excel, etc.).
import pandas as pd # Para lidar com tabelas de dados (tipo Excel).
from datetime import datetime # Para mexer com datas e horas.
from reportlab.lib.pagesizes import letter # Para gerar arquivos PDF do zero.
from reportlab.pdfgen import canvas

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
        # Converte as datas e calcula a diferença entre elas.
        entrada = datetime.strptime(str(entrada_str), "%Y-%m-%d %H:%M:%S")
        saida = datetime.strptime(str(saida_str), "%Y-%m-%d %H:%M:%S")
        return str(saida - entrada)
    except Exception:
        return "—"

# Função principal que consulta o banco e gera o relatório de presença com base nos filtros escolhidos.
def gerar_relatorio_presenca(data_inicio=None, data_fim=None, turno=None, turma=None, aluno=None, pagina=1, por_pagina=15):
    # Conecta no banco e cria um cursor que permite executar SQL.
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        filtros = [] # Lista onde vamos colocando os pedaços do WHERE da consulta.
        parametros = [] # Os valores que vão substituir os %s na query.

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

        # Aqui conta quantos resultados totais vão vir, pra saber quantas páginas precisa.
        count_query = f"SELECT COUNT(*) as total FROM ({query}) AS sub"
        cursor.execute(count_query, parametros)
        total = cursor.fetchone()['total']
        total_paginas = max(1, (total + por_pagina - 1) // por_pagina)

        #Aqui aplica o LIMIT e OFFSET pra trazer só os dados da página atual.
        offset = (pagina - 1) * por_pagina
        query += " LIMIT %s OFFSET %s"
        parametros.extend([por_pagina, offset])

        cursor.execute(query, parametros)
        registros = cursor.fetchall()

        conn.close()
        return registros, total_paginas

    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        conn.close()
        return [], 1

# Função que gera um PDF com os dados de presença organizados de forma simples e legível.
def gerar_pdf(registros):
    buffer = io.BytesIO() # Cria um espaço em memória pra armazenar o PDF.
    pdf = canvas.Canvas(buffer, pagesize=letter)
    largura, altura = letter

    # Título do PDF.
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(30, altura - 30, "Relatório de Presença")

    y = altura - 60
    pdf.setFont("Helvetica", 10)

    # Escreve os dados no PDF linha por linha.
    for reg in registros:
        texto = (
            f"Aluno: {reg['aluno']} | Turma: {reg['turma']} | Turno: {reg['turno']} | "
            f"Entrada: {reg['entrada']} | Saída: {reg['saida']} | Duração: {reg['duracao']}"
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


# Função que gera uma planilha Excel (.xlsx) com os registros de presença.
def gerar_excel(registros):
    df = pd.DataFrame(registros) # Transforma os dados em uma planilha (tabela).
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, sheet_name='Presenças') # Salva como Excel no buffer.
    buffer.seek(0)
    return buffer

# Função que gera um arquivo de texto simples com os registros (sem formatação, só o conteúdo).
def gerar_txt(registros):
    buffer = io.StringIO() # Cria um buffer de texto.
    for reg in registros:
        buffer.write(
            f"Aluno: {reg['aluno']} | Turma: {reg['turma']} | Turno: {reg['turno']} | "
            f"Entrada: {reg['entrada']} | Saída: {reg['saida']} | Duração: {reg['duracao']}\n"
        )
    buffer.seek(0)
    return io.BytesIO(buffer.getvalue().encode('utf-8')) # Retorna como arquivo pronto pra download.