from flask import Flask, render_template, Response
import cv2  # Biblioteca OpenCV para manipulação de vídeo e imagens.
import numpy as np # Biblioteca NumPy para operações matemáticas.
import face_recognition as fr # Biblioteca para reconhecimento facial.
import sys
import os
import webbrowser # Para abrir automaticamente o navegador.
import threading # Para executar tarefas paralelas.
import time # Para adicionar pausas na execução do código.
from flask_socketio import SocketIO # Biblioteca para comunicação em tempo real via WebSocket.

# Adiciona o caminho do diretório principal ao sys.path para permitir importações de módulos locais.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa as funções do módulo de reconhecimento facial.
from modulo1_reconhecimento.engine import get_rostos, registrar_ocorrencia

app = Flask(__name__) # Inicializa a aplicação Flask.
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading') # Configura o Flask-SocketIO para comunicação em tempo real.

# Carrega os rostos conhecidos e seus nomes a partir do banco de dados de imagens.
rostos_conhecidos, nomes_dos_rostos = get_rostos()
camera = cv2.VideoCapture(0) # Inicializa a captura da câmera (0 indica a webcam padrão do sistema).

# Evento WebSocket para detectar conexão do cliente.
@socketio.on('connect')
def handle_connect():
    print("✅ Cliente conectado ao WebSocket")

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
            
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, nome, (left, bottom + 25), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

            if nome != "Desconhecido":
                registrar_ocorrencia(nome)
                socketio.emit('alerta', {'mensagem': f"✅ Aluno {nome} reconhecido e registrado!"}, namespace='/')
            else:
                socketio.emit('alerta', {'mensagem': "⚠️ Rosto não reconhecido. Tente novamente!"}, namespace='/')

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gerar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

def abrir_navegador():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

# Ponto de entrada da aplicação.
if __name__ == "__main__":
    threading.Thread(target=abrir_navegador).start()
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, use_reloader=False)
