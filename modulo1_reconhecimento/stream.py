import cv2
import numpy as np
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import time

from .engine import get_rostos, registrar_ocorrencia, cosine_similarity, face_app

FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 10
SIMILARITY_THRESHOLD = 0.5
TEMPO_ESPERA_MINUTOS = 10

camera = None
camera_index = 0
streaming = False

rostos_conhecidos, infos_dos_rostos = get_rostos()
tempo_ultima_ocorrencia = {}
tempo_ultimo_alerta_desconhecido = datetime.min

def iniciar_camera(index=0):
    global camera, streaming, camera_index
    camera_index = index
    if not streaming:
        camera = cv2.VideoCapture(camera_index)
        if not camera or not camera.isOpened():
            raise RuntimeError(f"❌ Não foi possível acessar a câmera de índice {camera_index}.")
        streaming = True
        print(f"🎥 Webcam (índice {camera_index}) ligada")

def liberar_camera():
    global camera, streaming
    if camera and camera.isOpened():
        camera.release()
    camera = None
    streaming = False
    print("🎥 Webcam desligada")

def recarregar_embeddings():
    global rostos_conhecidos, infos_dos_rostos
    rostos_conhecidos, infos_dos_rostos = get_rostos()
    return len(rostos_conhecidos)

def desenhar_texto(frame, texto, posicao, cor=(255, 255, 255), cor_fundo=(0, 0, 0)):
    imagem_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(imagem_pil)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), texto, font=font)
    largura_texto = bbox[2] - bbox[0]
    altura_texto = bbox[3] - bbox[1]

    centro_x = posicao[0]
    y = posicao[1]

    x = int(centro_x - (largura_texto / 2))

    draw.rectangle([x - 3, y, x + largura_texto + 3, y + altura_texto + 4], fill=cor_fundo)
    draw.text((x, y + 2), texto, font=font, fill=cor)

    return np.array(imagem_pil)

def gerar_frames(socketio):
    global tempo_ultimo_alerta_desconhecido, camera, streaming

    if not streaming or camera is None or not camera.isOpened():
        print("⏹️ Transmissão não está ativa ou câmera não iniciada.")
        return

    tempo_frame_anterior = datetime.now()

    while streaming:
        if not camera or not camera.isOpened():
            print("⛔ Câmera foi desligada.")
            break

        sucesso, frame = camera.read()
        if not sucesso or frame is None:
            print("⚠️ Falha na leitura da câmera. Encerrando transmissão...")
            liberar_camera()
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

            similaridades = [cosine_similarity(embedding, ref) for ref in rostos_conhecidos]
            melhor_id = int(np.argmax(similaridades)) if similaridades else -1
            melhor_sim = similaridades[melhor_id] if melhor_id != -1 else 0

            if melhor_sim > SIMILARITY_THRESHOLD:
                info = infos_dos_rostos[melhor_id]
                nome = info["nome"]
                turma = info["turma"]
                texto_exibicao = f"{nome} ({turma})"
                cor = (0, 255, 0)

                if nome in tempo_ultima_ocorrencia and (agora - tempo_ultima_ocorrencia[nome]) < timedelta(minutes=TEMPO_ESPERA_MINUTOS):
                    mensagem = f"⏳ {texto_exibicao} já registrado recentemente! Ignorado..."
                    tipo = "info"
                else:
                    nome_padronizado = nome.strip().upper()
                    tipo_registro, mensagem = registrar_ocorrencia(nome_padronizado)
                    tempo_ultima_ocorrencia[nome] = agora
                    tipo = tipo_registro if tipo_registro in ["entrada", "saida"] else "info"

                socketio.emit('alerta', {
                    'mensagem': mensagem,
                    'nome': texto_exibicao,
                    'tipo': tipo
                }, namespace='/')

            else:
                texto_exibicao = "Desconhecido"
                cor = (0, 0, 255)

                if (agora - tempo_ultimo_alerta_desconhecido) > timedelta(seconds=5):
                    socketio.emit('alerta', {
                        'mensagem': "⚠️ Rosto não reconhecido! Registro não realizado...",
                        'nome': texto_exibicao,
                        'tipo': "erro"
                    }, namespace='/')
                    tempo_ultimo_alerta_desconhecido = agora

            cv2.rectangle(frame, (left, top), (right, bottom), cor, 2)
            meio_caixa = (left + right) // 2
            frame = desenhar_texto(frame, texto_exibicao, (meio_caixa, bottom + 10))

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
