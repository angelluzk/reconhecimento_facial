import cv2
import numpy as np
import time
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

from .engine import get_rostos, registrar_ocorrencia, cosine_similarity, face_app

# Configurações
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 10
SIMILARITY_THRESHOLD = 0.5
TEMPO_ESPERA_MINUTOS = 10

camera = cv2.VideoCapture(0)

rostos_conhecidos, nomes_dos_rostos = get_rostos()
tempo_ultima_ocorrencia = {}

def desenhar_texto(frame, texto, posicao, cor=(255, 255, 255), cor_fundo=(0, 0, 0)):
    imagem_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(imagem_pil)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), texto, font=font)
    largura_texto = bbox[2] - bbox[0]
    altura_texto = bbox[3] - bbox[1]

    x, y = posicao
    draw.rectangle([x, y, x + largura_texto + 6, y +
                   altura_texto + 4], fill=cor_fundo)
    draw.text((x + 3, y + 2), texto, font=font, fill=cor)

    return np.array(imagem_pil)

def gerar_frames(socketio):
    tempo_frame_anterior = datetime.now()

    while True:
        sucesso, frame = camera.read()
        if not sucesso:
            break

        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        agora = datetime.now()

        if (agora - tempo_frame_anterior).total_seconds() < 1.0 / FPS:
            time.sleep(0.01)
            continue
        tempo_frame_anterior = agora

        rostos_detectados = face_app.get(frame)

        for rosto in rostos_detectados:
            embedding = rosto.embedding
            bbox = rosto.bbox.astype(int)
            top, left, bottom, right = bbox[1], bbox[0], bbox[3], bbox[2]

            similaridades = [cosine_similarity(
                embedding, ref) for ref in rostos_conhecidos]
            melhor_id = int(np.argmax(similaridades)) if similaridades else -1
            melhor_sim = similaridades[melhor_id] if melhor_id != -1 else 0

            if melhor_sim > SIMILARITY_THRESHOLD:
                nome = nomes_dos_rostos[melhor_id]
                cor = (0, 255, 0)

                if nome in tempo_ultima_ocorrencia and (agora - tempo_ultima_ocorrencia[nome]) < timedelta(minutes=TEMPO_ESPERA_MINUTOS):
                    mensagem = f"⏳ {nome} já registrado recentemente. Ignorado."
                    tipo = "info"
                else:
                    tipo_registro, mensagem = registrar_ocorrencia(nome)
                    tempo_ultima_ocorrencia[nome] = agora
                    tipo = tipo_registro if tipo_registro in [
                        "entrada", "saida"] else "info"

                socketio.emit('alerta', {
                    'mensagem': mensagem,
                    'nome': nome,
                    'tipo': tipo
                }, namespace='/')
            else:
                nome = "Desconhecido"
                cor = (0, 0, 255)

                socketio.emit('alerta', {
                    'mensagem': "⚠️ Rosto não reconhecido! Registro não realizado.",
                    'nome': nome,
                    'tipo': "erro"
                }, namespace='/')

            cv2.rectangle(frame, (left, top), (right, bottom), cor, 2)
            frame = desenhar_texto(frame, nome, (left, bottom + 10))

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')