import os
import sys
import time
import threading
import webbrowser
from datetime import datetime, date, timedelta

from flask import Flask, render_template, Response, request, send_file
from flask_socketio import SocketIO, emit

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modulo1_reconhecimento.engine import get_rostos
from modulo1_reconhecimento.relatorios import (
    gerar_relatorio_presenca, gerar_pdf, gerar_excel, gerar_txt
)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y %H:%M:%S'):
    try:
        if isinstance(value, datetime):
            return value.strftime(format)
        elif isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime(format)
    except ValueError:
        pass
    return value

@socketio.on('connect')
def handle_connect():
    print("✅ Cliente conectado via WebSocket")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    from modulo1_reconhecimento.stream import gerar_frames
    return Response(gerar_frames(socketio), mimetype='multipart/x-mixed-replace; boundary=frame')

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

    formatos_validos = {
        'pdf': ('application/pdf', gerar_pdf, 'pdf'),
        'xlsx': ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', gerar_excel, 'xlsx'),
        'txt': ('text/plain', gerar_txt, 'txt'),
    }

    if formato not in formatos_validos:
        return "❌ Formato de relatório inválido.", 400

    mimetype, funcao_geradora, ext = formatos_validos[formato]
    buffer = funcao_geradora(registros)

    return send_file(buffer, mimetype=mimetype, as_attachment=True, download_name=f'relatorio_presenca.{ext}')

def abrir_navegador():
    time.sleep(2)
    try:
        webbrowser.open("http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Erro ao abrir navegador: {e}")

if __name__ == "__main__":
    threading.Thread(target=abrir_navegador).start()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)