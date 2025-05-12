import cv2
import numpy as np
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import time
import threading
import queue
from app.recognition.engine import (
    get_rostos, registrar_ocorrencia, cosine_similarity, face_app, formatar_nome_turma
)
from pathlib import Path

FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 10
SIMILARITY_THRESHOLD = 0.5
COR_RECONHECIDO = (0, 255, 0)
COR_DESCONHECIDO = (0, 0, 255)

camera = None
streaming = False
frame_queue = queue.Queue(maxsize=5)
resultados_queue = queue.Queue(maxsize=5)
stop_event = threading.Event()
camera_lock = threading.Lock()

rostos_conhecidos, infos_dos_rostos = get_rostos()
tempo_ultima_ocorrencia = {}
tempo_ultimo_alerta_desconhecido = datetime.min
threads_iniciadas = False

def iniciar_camera(index=0):
    global camera, streaming
    with camera_lock:
        if not streaming:
            try:
                camera = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
                if not camera or not camera.isOpened():
                    raise ValueError("Câmera não disponível")
                streaming = True
            except Exception as e:
                print(f"Erro ao iniciar a câmera: {e}")

def liberar_camera():
    global camera, streaming
    with camera_lock:
        if camera and camera.isOpened():
            camera.release()
        camera = None
        streaming = False

def recarregar_embeddings():
    global rostos_conhecidos, infos_dos_rostos
    rostos_conhecidos, infos_dos_rostos = get_rostos()
    return len(rostos_conhecidos)

def desenhar_texto_com_pil(frame, texto, posicao, cor=(255, 255, 255), cor_fundo=(0, 0, 0)):
    imagem_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(imagem_pil)

    font_path = str(Path("app/static/fonts/arial.ttf"))
    try:
        font = ImageFont.truetype(font_path, 18)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), texto, font=font)
    largura_texto = bbox[2] - bbox[0]
    altura_texto = bbox[3] - bbox[1]

    x = int(posicao[0] - (largura_texto / 2))
    y = posicao[1]

    draw.rectangle([x - 3, y, x + largura_texto + 3,
                   y + altura_texto + 4], fill=cor_fundo)
    draw.text((x, y + 2), texto, font=font, fill=cor)

    return np.array(imagem_pil)

def capturar_frames():
    while not stop_event.is_set():
        with camera_lock:
            if camera and camera.isOpened():
                sucesso, frame = camera.read()
                if sucesso and frame is not None:
                    if not frame_queue.full():
                        frame_queue.put(frame)
        time.sleep(1.0 / FPS)

def processar_frames(socketio):
    global tempo_ultimo_alerta_desconhecido
    ultimo_rosto = []
    tempo_ultimo_rosto = datetime.min

    while not stop_event.is_set():
        try:
            frame = frame_queue.get(timeout=0.5)
        except queue.Empty:
            continue

        agora = datetime.now()

        if (agora - tempo_ultimo_rosto).total_seconds() < 1.0:
            rostos_detectados = ultimo_rosto
        else:
            rostos_detectados = face_app.get(frame)
            ultimo_rosto = rostos_detectados if rostos_detectados else []
            tempo_ultimo_rosto = agora

        for rosto in rostos_detectados:
            embedding = rosto.embedding
            bbox = rosto.bbox.astype(int)
            top, left, bottom, right = bbox[1], bbox[0], bbox[3], bbox[2]

            similaridades = [cosine_similarity(embedding, ref) for ref in rostos_conhecidos]
            melhor_id = int(np.argmax(similaridades)) if similaridades else -1
            melhor_sim = similaridades[melhor_id] if melhor_id != -1 else 0

            if melhor_sim > SIMILARITY_THRESHOLD:
                info_base = infos_dos_rostos[melhor_id]
                nome = info_base["nome"]
                turma = info_base["turma"]
                texto_exibicao = formatar_nome_turma(nome, turma)

                tipo_registro, mensagem = registrar_ocorrencia(nome)
                tipo = tipo_registro if tipo_registro in ["entrada", "saida"] else "info"

                if mensagem:
                    socketio.emit('alerta', {
                        'mensagem': mensagem,
                        'nome': texto_exibicao,
                        'tipo': tipo
                    }, namespace='/')

                cor = COR_RECONHECIDO
            else:
                texto_exibicao = "Desconhecido"
                cor = COR_DESCONHECIDO
                if (agora - tempo_ultimo_alerta_desconhecido) > timedelta(seconds=5):
                    socketio.emit('alerta', {
                        'mensagem': "⚠️ Rosto não reconhecido! Registro não realizado...",
                        'nome': texto_exibicao,
                        'tipo': "erro"
                    }, namespace='/')
                    tempo_ultimo_alerta_desconhecido = agora

            cv2.rectangle(frame, (left, top), (right, bottom), cor, 2)

            meio_caixa = (left + right) // 2
            frame = desenhar_texto_com_pil(frame, texto_exibicao, (meio_caixa, bottom + 10))

        if not resultados_queue.full():
            resultados_queue.put(frame)

def gerar_frames(socketio):
    global threads_iniciadas
    stop_event.clear()

    if not threads_iniciadas:
        threading.Thread(target=capturar_frames, daemon=True).start()
        threading.Thread(target=processar_frames, args=(socketio,), daemon=True).start()
        threads_iniciadas = True

    try:
        while not stop_event.is_set():
            try:
                frame = resultados_queue.get(timeout=0.5)
                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            except queue.Empty:
                continue
    finally:
        liberar_camera()
        threads_iniciadas = False

def parar_streaming():
    stop_event.set()
    liberar_camera()