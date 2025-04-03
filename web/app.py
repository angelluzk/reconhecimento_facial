from flask import Flask, render_template, Response
import cv2  # OpenCV para manipulação de vídeo.
import numpy as np  # Biblioteca NumPy para cálculos matemáticos.
import face_recognition as fr  # Biblioteca para reconhecimento facial.
import sys
import os
import webbrowser  # Para abrir automaticamente o navegador.
import threading  # Para executar tarefas em paralelo.
import time  # Para pausas na execução.
from flask_socketio import SocketIO  # Comunicação em tempo real via WebSocket.
from PIL import Image, ImageDraw, ImageFont  # 🔹 Biblioteca para exibir texto com acentos.

# 🔹 Garante que o Python encontre o módulo database.connection.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 🔹 Importa funções do banco de dados e reconhecimento facial.
from database.connection import get_db_connection
from modulo1_reconhecimento.engine import get_rostos, registrar_ocorrencia

# 🔹 Inicializa Flask e SocketIO.
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 🔹 Carrega rostos e nomes dos alunos.
rostos_conhecidos, nomes_dos_rostos = get_rostos()
camera = cv2.VideoCapture(0)  # Captura da câmera.

# 🔹 Evento WebSocket para conexão do cliente.
@socketio.on('connect')
def handle_connect():
    print("✅ Cliente conectado ao WebSocket")

# 🔹 Função para desenhar texto corretamente.
def desenhar_texto(frame, text, position, font_path="arial.ttf", font_size=24):
    pil_img = Image.fromarray(frame)  # Converte frame para PIL.
    draw = ImageDraw.Draw(pil_img)

    try:
        font = ImageFont.truetype(font_path, font_size)  # Usa a fonte Arial.
    except IOError:
        font = ImageFont.load_default()  # Usa fonte padrão se Arial não estiver disponível.

    draw.text(position, text, font=font, fill=(255, 255, 255, 255))
    return np.array(pil_img)  # Converte de volta para OpenCV.

# 🔹 Função de reconhecimento facial.
def gerar_frames():
    while True:
        sucesso, frame = camera.read()
        if not sucesso:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        localizacao_dos_rostos = fr.face_locations(rgb_frame)
        rostos_desconhecidos = fr.face_encodings(rgb_frame, localizacao_dos_rostos)

        for (top, right, bottom, left), rosto_desconhecido in zip(localizacao_dos_rostos, rostos_desconhecidos):
            face_distances = fr.face_distance(rostos_conhecidos, rosto_desconhecido)
            melhor_id = np.argmin(face_distances) if len(face_distances) > 0 else -1
            nome = nomes_dos_rostos[melhor_id] if melhor_id != -1 and fr.compare_faces(rostos_conhecidos, rosto_desconhecido)[melhor_id] else "Desconhecido"

            # 🔹 Desenha retângulo ao redor do rosto.
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # 🔹 Desenha o nome corretamente com acentos.
            frame = desenhar_texto(frame, nome, (left, bottom + 10))

            # 🔹 Registra a ocorrência se for um aluno conhecido.
            if nome != "Desconhecido":
                registrar_ocorrencia(nome)
                socketio.emit('alerta', {'mensagem': f"✅ Aluno {nome} reconhecido e registrado!"}, namespace='/')
            else:
                socketio.emit('alerta', {'mensagem': "⚠️ Rosto não reconhecido. Tente novamente!"}, namespace='/')

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# 🔹 Rota para fornecer vídeo ao vivo.
@app.route('/video_feed')
def video_feed():
    return Response(gerar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 🔹 Página principal.
@app.route('/')
def index():
    return render_template('index.html')

# 🔹 Abre o navegador automaticamente.
def abrir_navegador():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

# 🔹 Inicia a aplicação.
if __name__ == "__main__":
    threading.Thread(target=abrir_navegador).start()
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, use_reloader=False)
