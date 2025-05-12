import os
from flask import (
    Blueprint, request, jsonify, render_template, send_from_directory
)
from app.services.alunos_service import (
    atualizar_aluno, excluir_aluno, listar_alunos, processar_cadastro_web
)
from app.recognition.stream import (
    liberar_camera, iniciar_camera, recarregar_embeddings, streaming
)
from app.utils.caminhos import FOTOS_ALUNOS_DIR

alunos_bp = Blueprint('alunos', __name__)

@alunos_bp.route('/fotos_alunos/<path:filename>')
def servir_foto_aluno(filename):
    try:
        caminho_arquivo = os.path.join(FOTOS_ALUNOS_DIR, filename)

        if os.path.exists(caminho_arquivo):
            return send_from_directory(FOTOS_ALUNOS_DIR, filename)
        else:
            print(f"❌ Arquivo não encontrado: {filename}")
            return "Arquivo não encontrado", 404
    except Exception as e:
        print(f"❌ Erro ao tentar servir foto: {e}")
        return "Erro ao tentar servir foto", 500

@alunos_bp.route('/')
def cadastro():
    return render_template('cadastrar_alunos.html')


@alunos_bp.route('/cadastrar_aluno', methods=['POST'])
def cadastrar_aluno():
    try:
        nome = request.form['nome']
        turno = request.form['turno']
        ano = request.form['ano']
        turma = request.form['turma']
        index = int(request.form.get('index', '1'))
        imagem_bytes = request.files['foto'].read()

        resultado = processar_cadastro_web(
            nome, ano, turma, turno, imagem_bytes, index)

        if not resultado["sucesso"]:
            return jsonify({"erro": resultado["mensagem"]}), 400

        if index == 10:
            total = recarregar_embeddings()
            print(f"🔄 {total} embeddings recarregados após cadastro de {nome}")

        return jsonify({"sucesso": True})
    except Exception as e:
        print(f"❌ Erro ao cadastrar aluno: {e}")
        return jsonify({"erro": "Erro ao cadastrar aluno."}), 500


@alunos_bp.route('/recarregar_embeddings', methods=['POST'])
def atualizar_embeddings():
    try:
        if streaming:
            liberar_camera()
            iniciar_camera()
        total = recarregar_embeddings()
        return jsonify({"mensagem": f"{total} embeddings recarregados com sucesso. A câmera foi reiniciada."})
    except Exception as e:
        print(f"❌ Erro ao recarregar embeddings: {e}")
        return jsonify({"erro": "Erro ao recarregar embeddings."}), 500


@alunos_bp.route('/alunos', methods=['GET'])
def alunos():
    turno = request.args.get('turno')
    ano = request.args.get('ano')
    turma = request.args.get('turma')
    nome = request.args.get('nome')
    pagina = int(request.args.get('pagina', 1))

    turma_completa = f"{ano} {turma}".strip() if ano and turma else None

    alunos, total_alunos = listar_alunos(
        turno=turno, turma=turma_completa, nome=nome, pagina=pagina)

    alunos_por_pagina = 10
    total_paginas = (total_alunos // alunos_por_pagina) + \
        (1 if total_alunos % alunos_por_pagina > 0 else 0)

    return render_template('alunos.html', alunos=alunos, pagina_atual=pagina, total_paginas=total_paginas)


@alunos_bp.route('/api/alunos', methods=['GET'])
def get_alunos():
    turno = request.args.get('turno')
    ano = request.args.get('ano')
    turma = request.args.get('turma')
    nome = request.args.get('nome')
    pagina = int(request.args.get('pagina', 1))
    alunos_por_pagina = 10

    turma_completa = f"{ano} {turma}".strip() if ano and turma else None

    alunos, total_alunos = listar_alunos(
        turno=turno, turma=turma_completa, nome=nome, pagina=pagina, alunos_por_pagina=alunos_por_pagina)

    total_paginas = (total_alunos // alunos_por_pagina) + \
        (1 if total_alunos % alunos_por_pagina > 0 else 0)

    return jsonify({
        'alunos': alunos,
        'total_paginas': total_paginas,
        'pagina_atual': pagina
    })


@alunos_bp.route('/api/alunos/<int:id_aluno>', methods=['PUT'])
def put_aluno(id_aluno):
    try:
        aluno = request.get_json()

        ano = aluno.get('ano', '')
        turma = aluno.get('turma', '')
        nome = aluno.get('nome')
        turno = aluno.get('turno')

        if not nome or not turno:
            return jsonify({"sucesso": False, "mensagem": "Nome e turno são obrigatórios."}), 400

        resultado = atualizar_aluno(id_aluno, nome, turno, ano, turma)

        if resultado["sucesso"]:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400

    except Exception as e:
        print(f"[ERRO] Erro ao atualizar aluno: {e}")
        return jsonify({"sucesso": False, "mensagem": "Erro ao atualizar aluno."}), 500


@alunos_bp.route('/api/alunos/<int:id_aluno>', methods=['DELETE'])
def delete_aluno(id_aluno):
    resultado = excluir_aluno(id_aluno)
    return jsonify(resultado)