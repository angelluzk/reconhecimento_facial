from flask import (
    Blueprint, request, render_template, send_file
)
from io import BytesIO
from datetime import date, timedelta
from app.services.relatorios_service import (
    gerar_relatorio_presenca, gerar_pdf, gerar_excel, gerar_txt
)

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/relatorios', endpoint='relatorios')
def relatorios():
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    turno = request.args.get('turno', '')
    ano = request.args.get('ano', '')
    turma = request.args.get('turma', '')
    turma_completa = f"{ano} {turma}".strip() if ano and turma else ''
    aluno = request.args.get('aluno', '')
    semana_atual = request.args.get('semana_atual', '')

    pagina = int(request.args.get('pagina', 1))
    por_pagina = 10
    if semana_atual:
        hoje = date.today()
        data_inicio = (hoje - timedelta(days=hoje.weekday())
                       ).strftime('%Y-%m-%d')
        data_fim = (hoje + timedelta(days=6 - hoje.weekday())
                    ).strftime('%Y-%m-%d')

    try:
        registros, total_paginas = gerar_relatorio_presenca(
            data_inicio, data_fim, turno, turma_completa, aluno, pagina, por_pagina
        )
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        registros = []
        total_paginas = 1

    return render_template(
        'relatorio.html',
        registros=registros,
        pagina_atual=pagina,
        total_paginas=total_paginas,
        data_inicio=data_inicio,
        data_fim=data_fim,
        turno=turno,
        turma=turma,
        ano=ano,
        aluno=aluno
    )


@relatorios_bp.route('/baixar_relatorio/<formato>')
def baixar_relatorio(formato):
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    turno = request.args.get('turno', '')
    ano = request.args.get('ano', '')
    turma = request.args.get('turma', '')
    turma_completa = f"{ano} {turma}".strip() if ano and turma else ''
    aluno = request.args.get('aluno', '')

    pagina = request.args.get('pagina', None, type=int)
    por_pagina = request.args.get('por_pagina', None, type=int)

    registros, _ = gerar_relatorio_presenca(
        data_inicio, data_fim, turno, turma_completa, aluno, pagina, por_pagina
    )

    filtros_usados = {
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "turno": turno,
        "turma": turma_completa,
        "aluno": aluno
    }

    print("🛠️ Filtros recebidos:", filtros_usados)

    formatos = {
        'pdf': ('application/pdf', gerar_pdf, 'pdf'),
        'xlsx': ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', gerar_excel, 'xlsx'),
        'txt': ('text/plain', gerar_txt, 'txt'),
    }

    if formato not in formatos:
        return "❌ Formato inválido!", 400

    mimetype, funcao, ext = formatos[formato]
    output = funcao(registros, filtros=filtros_usados)

    if isinstance(output, BytesIO):
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name=f"relatorio_presencas.{ext}",
            mimetype=mimetype
        )

    return "❌ Erro ao gerar o relatório", 500