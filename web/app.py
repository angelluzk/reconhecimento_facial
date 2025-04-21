 #Este arquivo contém a configuração e as rotas principais de um aplicativo Flask para reconhecimento facial e gerenciamento de alunos.

# Importação das bibliotecas necessárias.
import os
import sys
import time
import threading
import webbrowser
from datetime import datetime, date, timedelta
from flask import Flask, render_template, Response, request, jsonify, send_from_directory, send_file
from flask_socketio import SocketIO

# Adiciona o diretório superior ao caminho de módulos, para importar os módulos corretamente.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importação de funções específicas de outros módulos.
from modulo1_reconhecimento.controle_tempo import obter_configuracao_tempo, atualizar_configuracao_tempo
from modulo1_reconhecimento.crud_alunos import listar_alunos, atualizar_aluno, excluir_aluno
from database.connection import get_db_connection
from modulo1_reconhecimento.cadastro import processar_cadastro_web
from modulo1_reconhecimento.stream import gerar_frames, recarregar_embeddings, iniciar_camera, liberar_camera
from modulo1_reconhecimento.relatorios import gerar_relatorio_presenca, gerar_pdf, gerar_excel, gerar_txt
from modulo1_reconhecimento.engine import carregar_face_model

# Criação da instância do aplicativo Flask.
app = Flask(__name__)
# Criação da instância do SocketIO para comunicação em tempo real via WebSockets.
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Variáveis globais para controle do estado da webcam.
webcam_ativa = False
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FOTOS_ALUNOS_DIR = os.path.join(
    BASE_DIR, "modulo1_reconhecimento", "fotos_alunos")
REQUIRED_DIRS = [
    "modulo1_reconhecimento/fotos_alunos",
    "modulo1_reconhecimento/embeddings_cache"
]

# Verifica a existência de diretórios necessários e os cria, se não existirem.
for path in REQUIRED_DIRS:
    os.makedirs(path, exist_ok=True)
    print(f"📁 Verificado/criado: {path}")

# Carrega o modelo de reconhecimento facial.
model = carregar_face_model()

# Define um filtro para formatação de datas no template.
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y'):
    from datetime import datetime

    try:
        if isinstance(value, datetime):
            return value.strftime(format)
        elif isinstance(value, str):
            # Tenta converter primeiro com hora.
            try:
                return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime(format)
            except ValueError:
                # Se não tiver hora, tenta só com a data.
                return datetime.strptime(value, '%Y-%m-%d').strftime(format)
    except Exception:
        return value

# Evento de conexão do SocketIO, indica que o cliente se conectou via WebSocket.
@socketio.on('connect')
def conectar():
    print("✅ Cliente conectado via WebSocket.")

# Rota para renderizar a página principal.
@app.route('/')
def index():
    return render_template('index.html')

# Rota que retorna o feed de vídeo, enviando frames via streaming.
@app.route('/video_feed')
def video_feed():
    from modulo1_reconhecimento.stream import camera
    # Verifica se a câmera está aberta, e se sim, transmite os frames.
    if camera and camera.isOpened():
        return Response(gerar_frames(socketio), mimetype='multipart/x-mixed-replace; boundary=frame')
    return '', 204

# Rota para obter o tempo de espera da configuração.
@app.route('/api/tempo-espera', methods=['GET'])
def get_tempo_espera():
    config = obter_configuracao_tempo()
    if config:
        return jsonify({"valor": int(config["valor"]), "tipo": config["tipo"]})
    return jsonify({"error": "Configuração não encontrada"}), 404

# Rota para definir o tempo de espera da configuração.
@app.route('/api/tempo-espera', methods=['POST'])
def set_tempo_espera():
    data = request.get_json()
    valor = data.get("valor")
    tipo = data.get("tipo")
    # Valida os dados recebidos antes de atualizar a configuração.
    if valor and tipo in ["minutos", "horas"]:
        atualizar_configuracao_tempo(valor, tipo)
        return jsonify({"message": "Configuração atualizada com sucesso"})
    return jsonify({"error": "Dados inválidos"}), 400

# Rota para alternar o estado da webcam (ligar/desligar).
@app.route('/toggle_stream', methods=['POST'])
def toggle_stream():
    global webcam_ativa
    try:
        if not webcam_ativa:
            iniciar_camera() # Inicia a câmera.
            webcam_ativa = True
            print("🎥 Webcam ligada!")
        else:
            liberar_camera() # Desliga a câmera.
            webcam_ativa = False
            print("🎥 Webcam desligada!")
        return jsonify({'ativo': webcam_ativa})
    except Exception as e:
        print(f"❌ Erro ao alternar webcam: {e}")
        return jsonify({'erro': 'Erro ao alternar webcam'}), 500

# Rota para desligar a câmera manualmente.
@app.route('/desligar_camera', methods=['POST'])
def desligar_camera():
    global webcam_ativa
    try:
        if webcam_ativa:
            liberar_camera() # Desliga a câmera.
            webcam_ativa = False
            print("🔌 Webcam desligada por mudança de página!")
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"❌ Erro ao desligar webcam: {e}")
        return jsonify({'erro': 'Erro ao desligar webcam'}), 500

# Rota para gerar relatórios, com filtros de data, turno, ano, turma e aluno.
@app.route('/relatorios')
def relatorios():
        # Obtém parâmetros da query string da URL.
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    turno = request.args.get('turno', '')
    ano = request.args.get('ano', '')
    turma = request.args.get('turma', '')
    turma_completa = f"{ano} {turma}".strip() if ano and turma else ''
    aluno = request.args.get('aluno', '')
    semana_atual = request.args.get('semana_atual', '')

    pagina = int(request.args.get('pagina', 1))
    por_pagina = 15
    if semana_atual:
        # Se for semana atual, ajusta as datas de início e fim para a semana corrente.
        hoje = date.today()
        data_inicio = (hoje - timedelta(days=hoje.weekday())
                       ).strftime('%Y-%m-%d')
        data_fim = (hoje + timedelta(days=6 - hoje.weekday())
                    ).strftime('%Y-%m-%d')

    try:
        # Chama a função para gerar o relatório com os parâmetros.
        registros, total_paginas = gerar_relatorio_presenca(
            data_inicio, data_fim, turno, turma_completa, aluno, pagina, por_pagina
        )
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        registros = []
        total_paginas = 1

    # Retorna a página de relatórios com os dados gerados.
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

# Rota para baixar os relatórios em diferentes formatos (PDF, Excel, TXT).
@app.route('/baixar_relatorio/<formato>')
def baixar_relatorio(formato):
    # Obtém parâmetros da query string da URL.
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    turno = request.args.get('turno', 'Todos')
    ano = request.args.get('ano', '')
    turma = request.args.get('turma', '')
    turma_completa = f"{ano} {turma}".strip() if ano and turma else ''
    aluno = request.args.get('aluno', '')

    # Paginação (opcional, se não precisar de paginação, define None).
    pagina = request.args.get('pagina', None, type=int)  # Mudei de 1 para None.
    por_pagina = request.args.get('por_pagina', None, type=int)  # Mudei de 10 para None.

    # Chama a função para gerar o relatório de presença com os parâmetros.
    registros, total_paginas = gerar_relatorio_presenca(
        data_inicio, data_fim, turno, turma_completa, aluno, pagina, por_pagina
    )

    # Define os formatos de arquivo disponíveis para download.
    formatos = {
        'pdf': ('application/pdf', gerar_pdf, 'pdf'),
        'xlsx': ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', gerar_excel, 'xlsx'),
        'txt': ('text/plain', gerar_txt, 'txt'),
    }

    # Verifica se o formato é válido.
    if formato not in formatos:
        return "❌ Formato inválido!!", 400

    # Obtém as informações de tipo MIME e função para gerar o relatório no formato escolhido.
    mimetype, funcao, ext = formatos[formato]
    # Se for PDF, envia os filtros também para o cabeçalho.
    if formato == 'pdf' or formato == 'xlsx' or formato == 'txt':
        filtros_usados = {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "turno": turno,
            "turma": turma_completa,
            "aluno": aluno
        }
        buffer = funcao(registros, filtros=filtros_usados)
    else:
        buffer = funcao(registros)

    # Retorna o arquivo gerado para download.
    return send_file(buffer, mimetype=mimetype, as_attachment=True, download_name=f"relatorio.{ext}")

# Rota para renderizar a página de cadastro de alunos.
@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

# Rota para listar alunos, com filtros de turno, ano e turma.
@app.route('/alunos', methods=['GET'])
def alunos():
    turno = request.args.get('turno')
    ano = request.args.get('ano')
    turma = request.args.get('turma')
    nome = request.args.get('nome')
    pagina = int(request.args.get('pagina', 1))

    turma_completa = f"{ano} {turma}".strip() if ano and turma else None
    alunos, total_alunos = listar_alunos(turno=turno, turma=turma_completa, nome=nome, pagina=pagina)
    
    # Cálculo de total de páginas.
    alunos_por_pagina = 10
    total_paginas = (total_alunos // alunos_por_pagina) + (1 if total_alunos % alunos_por_pagina > 0 else 0)

    return render_template('alunos.html', alunos=alunos, pagina_atual=pagina, total_paginas=total_paginas)

# Rota de Cadastro de Aluno.
@app.route('/cadastrar_aluno', methods=['POST'])
def cadastrar_aluno():
    try:
        # Obtém os dados do aluno a partir do formulário.
        nome = request.form['nome']
        turno = request.form['turno']
        ano = request.form['ano']
        turma = request.form['turma']
        index = int(request.form.get('index', '1'))
        imagem_bytes = request.files['foto'].read()

        # Processa o cadastro de aluno, com a foto e dados informados.
        processar_cadastro_web(nome, ano, turma, turno, imagem_bytes, index)

        # Se o índice for 10, recarrega os embeddings para treinamento.
        if index == 10:
            total = recarregar_embeddings()
            print(f"🔄 {total} embeddings recarregados após cadastro de {nome}")

        return jsonify({"sucesso": True})
    except Exception as e:
        print(f"❌ Erro ao cadastrar aluno(a): {e}")
        return jsonify({"erro": "Erro ao cadastrar aluno(a)."}), 500

# Rota de Recarregar Embeddings.
@app.route('/recarregar_embeddings', methods=['POST'])
def atualizar_embeddings():
    try:
        total = recarregar_embeddings()
        return jsonify({"mensagem": f"{total} embeddings recarregados com sucesso."})
    except Exception as e:
        print(f"❌ Erro ao recarregar embeddings: {e}")
        return jsonify({"erro": "Erro ao recarregar embeddings."}), 500

# Rota para Detalhes de um Aluno.
@app.route('/detalhes_aluno/<int:id_aluno>')
def detalhes_aluno(id_aluno):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM alunos WHERE id = %s", (id_aluno,))
        aluno = cursor.fetchone()

        cursor.execute("""SELECT data_hora, tipo 
                          FROM registros_presenca 
                          WHERE id_aluno = %s 
                          ORDER BY data_hora DESC LIMIT 10""", (id_aluno,))
        historico = cursor.fetchall()

        return jsonify({"aluno": aluno, "historico": historico})
    except Exception as e:
        print(f"❌ Erro ao buscar detalhes do aluno(a): {e}")
        return jsonify({"erro": "Erro ao buscar dados"}), 500

# Rota de Consulta de Alunos via API.
@app.route('/api/alunos', methods=['GET'])
def get_alunos():
    turno = request.args.get('turno')
    ano = request.args.get('ano')
    turma = request.args.get('turma')
    nome = request.args.get('nome')
    pagina = int(request.args.get('pagina', 1))
    alunos_por_pagina = 10

    turma_completa = f"{ano} {turma}".strip() if ano and turma else None
    alunos, total_alunos = listar_alunos(turno=turno, turma=turma_completa, nome=nome, pagina=pagina, alunos_por_pagina=alunos_por_pagina)

    total_paginas = (total_alunos // alunos_por_pagina) + (1 if total_alunos % alunos_por_pagina > 0 else 0)

    return jsonify({
        'alunos': alunos,
        'total_paginas': total_paginas,
        'pagina_atual': pagina
    })

# Rota de Atualização de Aluno via API.
@app.route('/api/alunos/<int:id_aluno>', methods=['PUT'])
def put_aluno(id_aluno):
    nome = request.json['nome']
    turno = request.json['turno']
    turma = request.json['turma']
    foto_path = request.json.get('foto', None)

    resultado = atualizar_aluno(id_aluno, nome, turno, turma, foto_path)
    return jsonify(resultado)

# Rota de Exclusão de Aluno via API.
@app.route('/api/alunos/<int:id_aluno>', methods=['DELETE'])
def delete_aluno(id_aluno):
    resultado = excluir_aluno(id_aluno)
    return jsonify(resultado)

# Rota para Servir Foto de Aluno.
@app.route('/fotos_alunos/<path:filename>')
def servir_foto_aluno(filename):
    try:
        if os.path.exists(os.path.join(FOTOS_ALUNOS_DIR, filename)):
            return send_from_directory(FOTOS_ALUNOS_DIR, filename)
        else:
            print(f"❌ Arquivo não encontrado: {filename}")
            return "Arquivo não encontrado", 404
    except Exception as e:
        print(f"❌ Erro ao tentar servir foto: {e}")
        return "Erro ao tentar servir foto", 500

# Função para Abrir o Navegador.
def abrir_navegador():
    time.sleep(2)
    try:
        webbrowser.open("http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Erro ao abrir navegador: {e}")
        
# Execução do Servidor.
if __name__ == '__main__':
    threading.Thread(target=abrir_navegador).start()
    socketio.run(app, host='0.0.0.0', port=5000,
                 debug=True, use_reloader=False)