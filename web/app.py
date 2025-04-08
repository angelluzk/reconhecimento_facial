import os
import sys
import time
import threading
import webbrowser
from datetime import datetime, date, timedelta

from flask import Flask, render_template, Response, request, send_file, jsonify
from flask_socketio import SocketIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modulo1_reconhecimento.engine import carregar_face_model
from modulo1_reconhecimento.relatorios import (
    gerar_relatorio_presenca, gerar_pdf, gerar_excel, gerar_txt
)
from modulo1_reconhecimento.stream import (
    gerar_frames, recarregar_embeddings, iniciar_camera, liberar_camera
)
from modulo1_reconhecimento.cadastro import processar_cadastro_web
from database.connection import get_db_connection

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

webcam_ativa = False

REQUIRED_DIRS = [
    "modulo1_reconhecimento/fotos_alunos",
    "modulo1_reconhecimento/embeddings_cache"
]
for path in REQUIRED_DIRS:
    os.makedirs(path, exist_ok=True)
    print(f"📁 Verificado/criado: {path}")

model = carregar_face_model()

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y %H:%M:%S'):
    try:
        if isinstance(value, datetime):
            return value.strftime(format)
        elif isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime(format)
    except:
        return value
    return value

@socketio.on('connect')
def conectar():
    print("✅ Cliente conectado via WebSocket.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    from modulo1_reconhecimento.stream import camera
    if camera is not None and camera.isOpened():
        return Response(gerar_frames(socketio), mimetype='multipart/x-mixed-replace; boundary=frame')
    return '', 204

@app.route('/toggle_stream', methods=['POST'])
def toggle_stream():
    global webcam_ativa
    try:
        if not webcam_ativa:
            iniciar_camera()
            webcam_ativa = True
            print("🎥 Webcam ligada!")
        else:
            liberar_camera()
            webcam_ativa = False
            print("🎥 Webcam desligada!")
        return jsonify({'ativo': webcam_ativa})
    except Exception as e:
        print(f"❌ Erro ao alternar webcam: {e}")
        return jsonify({'erro': 'Erro ao alternar webcam'}), 500
    
@app.route('/desligar_camera', methods=['POST'])
def desligar_camera():
    global webcam_ativa
    try:
        if webcam_ativa:
            liberar_camera()
            webcam_ativa = False
            print("🔌 Webcam desligada por mudança de página!")
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"❌ Erro ao desligar webcam: {e}")
        return jsonify({'erro': 'Erro ao desligar webcam'}), 500

@app.route('/relatorios')
def relatorios():
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    turno = request.args.get('turno', '')
    turma = request.args.get('turma', '')
    aluno = request.args.get('aluno', '')
    semana_atual = request.args.get('semana_atual', '')

    if semana_atual:
        hoje = date.today()
        data_inicio = (hoje - timedelta(days=hoje.weekday())).strftime('%Y-%m-%d')
        data_fim = (hoje + timedelta(days=6 - hoje.weekday())).strftime('%Y-%m-%d')

    try:
        registros = gerar_relatorio_presenca(data_inicio, data_fim, turno, turma, aluno)
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        registros = []

    return render_template('relatorio.html', registros=registros)

@app.route('/baixar_relatorio/<formato>')
def baixar_relatorio(formato):
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    turno = request.args.get('turno', 'Todos')
    turma = request.args.get('turma', '')
    aluno = request.args.get('aluno', '')

    registros = gerar_relatorio_presenca(data_inicio, data_fim, turno, turma, aluno)

    formatos = {
        'pdf': ('application/pdf', gerar_pdf, 'pdf'),
        'xlsx': ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', gerar_excel, 'xlsx'),
        'txt': ('text/plain', gerar_txt, 'txt'),
    }

    if formato not in formatos:
        return "❌ Formato inválido!!", 400

    mimetype, funcao, ext = formatos[formato]
    buffer = funcao(registros)

    return send_file(buffer, mimetype=mimetype, as_attachment=True, download_name=f"relatorio.{ext}")

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/cadastrar_aluno', methods=['POST'])
def cadastrar_aluno():
    try:
        nome = request.form['nome']
        turno = request.form['turno']
        turma = request.form['turma']
        index = int(request.form.get('index', '1'))
        imagem_bytes = request.files['foto'].read()

        processar_cadastro_web(nome, turma, turno, imagem_bytes, index)

        if index == 10:
            total = recarregar_embeddings()
            print(f"🔄 {total} embeddings recarregados após cadastro de {nome}")

        return jsonify({"sucesso": True})
    except Exception as e:
        print(f"❌ Erro ao cadastrar aluno: {e}")
        return jsonify({"erro": "Erro ao cadastrar aluno."}), 500

@app.route('/recarregar_embeddings', methods=['POST'])
def atualizar_embeddings():
    try:
        total = recarregar_embeddings()
        return jsonify({"mensagem": f"{total} embeddings recarregados com sucesso."})
    except Exception as e:
        print(f"❌ Erro ao recarregar embeddings: {e}")
        return jsonify({"erro": "Erro ao recarregar embeddings."}), 500

@app.route('/detalhes_aluno/<int:aluno_id>')
def detalhes_aluno(aluno_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM alunos WHERE id = %s", (aluno_id,))
        aluno = cursor.fetchone()

        cursor.execute("""
            SELECT data_hora, tipo 
            FROM registros_presenca 
            WHERE aluno_id = %s 
            ORDER BY data_hora DESC LIMIT 10
        """, (aluno_id,))
        historico = cursor.fetchall()

        return jsonify({"aluno": aluno, "historico": historico})
    except Exception as e:
        print(f"❌ Erro ao buscar detalhes do aluno: {e}")
        return jsonify({"erro": "Erro ao buscar dados"}), 500

def abrir_navegador():
    time.sleep(2)
    try:
        webbrowser.open("http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Erro ao abrir navegador: {e}")

if __name__ == '__main__':
    threading.Thread(target=abrir_navegador).start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)