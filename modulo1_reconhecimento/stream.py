# Gerencia a captura de vídeo e o reconhecimento facial em tempo real.

import cv2 # Para capturar imagens da câmera e manipular vídeo.
import numpy as np # Para trabalhar com arrays numéricos.
from datetime import datetime, timedelta # Para trabalhar com datas e tempos.
from PIL import Image, ImageDraw, ImageFont # Para desenhar texto no frame com mais controle.
import time # Para controlar intervalos de tempo.

# Importa funções criadas em outros arquivos do projeto.
from .engine import get_rostos, registrar_ocorrencia, cosine_similarity, face_app, obter_tempo_espera
from .crud_alunos import obter_dados_aluno_com_cache

# Constantes que definem o tamanho do frame e a taxa de atualização (frames por segundo).
FRAME_WIDTH = 640 # Largura do vídeo.
FRAME_HEIGHT = 480 # Altura do vídeo.
FPS = 10 # Quantos frames por segundo processar.
SIMILARITY_THRESHOLD = 0.5 # Similaridade mínima para considerar uma face reconhecida.

# Variáveis de controle da câmera.
camera = None
camera_index = 0
streaming = False

# Carrega os embeddings (vetores de rosto), dos rostos conhecidos e suas informações relacionadas.
rostos_conhecidos, infos_dos_rostos = get_rostos()

# Controle de tempo para evitar registros duplicados em curto período.
tempo_ultima_ocorrencia = {}
tempo_ultimo_alerta_desconhecido = datetime.min

# Função que inicia a câmera no índice especificado. Se já estiver ativa, não faz nada.
def iniciar_camera(index=0):
    global camera, streaming, camera_index
    camera_index = index
    if not streaming:
        camera = cv2.VideoCapture(camera_index)
        if not camera or not camera.isOpened():
            raise RuntimeError(f"❌ Não foi possível acessar a câmera de índice {camera_index}.")
        streaming = True
        print(f"🎥 Webcam (índice {camera_index}) ligada")

# Função que libera a câmera e marca a transmissão com inativa.
def liberar_camera():
    global camera, streaming
    if camera and camera.isOpened():
        camera.release()
    camera = None
    streaming = False
    print("🎥 Webcam desligada")

# Função que recarrega os rostos conhecidos (útil quando um novo aluno é adicionado).
def recarregar_embeddings():
    global rostos_conhecidos, infos_dos_rostos
    rostos_conhecidos, infos_dos_rostos = get_rostos()
    return len(rostos_conhecidos)

# Função que desenha um texto centralizado com fundo no frame (usando PIL para melhor visual).
def desenhar_texto(frame, texto, posicao, cor=(255, 255, 255), cor_fundo=(0, 0, 0)):
    # Converte o frame do OpenCV (NumPy array) para uma imagem do tipo PIL.
    imagem_pil = Image.fromarray(frame)
    # Cria um objeto para desenhar na imagem PIL.
    draw = ImageDraw.Draw(imagem_pil)
    try:
        # Tenta carregar a fonte Arial com tamanho 18.
        font = ImageFont.truetype("arial.ttf", 18)
    except IOError:
        # Se não encontrar a fonte Arial, usa a fonte padrão.
        font = ImageFont.load_default()

    # Calcula a área que o texto vai ocupar (bounding box).
    bbox = draw.textbbox((0, 0), texto, font=font)
    largura_texto = bbox[2] - bbox[0] # Largura do texto.
    altura_texto = bbox[3] - bbox[1] # Altura do texto.

    # Posição central fornecida.
    centro_x = posicao[0]
    y = posicao[1]

    # Calcula a coordenada X para centralizar o texto horizontalmente.
    x = int(centro_x - (largura_texto / 2))

    # Desenha um retângulo de fundo atrás do texto (um pouco maior que o texto).
    draw.rectangle([x - 3, y, x + largura_texto + 3, y + altura_texto + 4], fill=cor_fundo)
    # Escreve o texto por cima do retângulo. 
    draw.text((x, y + 2), texto, font=font, fill=cor)

    # Converte a imagem de volta para array NumPy (para uso com OpenCV novamente).
    return np.array(imagem_pil)

# Função do loop principal que captura frames da câmera, detecta rostos e envia alertas. Também envia os frames com anotações (nome do aluno, ou 'Desconhecido') para o navegador.
def gerar_frames(socketio):
    global tempo_ultimo_alerta_desconhecido, camera, streaming

    # Verifica se a transmissão está ativa.
    if not streaming or camera is None or not camera.isOpened():
        print("⏹️ Transmissão não está ativa ou câmera não iniciada.")
        return

    tempo_frame_anterior = datetime.now()
    frame_counter = 0
    frame_interval = 3 # Detecta rostos a cada 3 frames.

    ultimo_rosto = []
    tempo_ultimo_rosto = datetime.min

    while streaming:
        # Se a câmera for desconectada durante a execução.
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

         # Controla o FPS.
        if (agora - tempo_frame_anterior).total_seconds() < 1.0 / FPS:
            time.sleep(0.01)
            continue
        tempo_frame_anterior = agora
        frame_counter += 1

         # Só detecta rostos a cada "frame_interval" frames.
        if frame_counter % frame_interval == 0:
            rostos_detectados = face_app.get(frame)
            if rostos_detectados:
                ultimo_rosto = rostos_detectados
                tempo_ultimo_rosto = agora
        else:
            # Usa o último rosto detectado, se for recente.
            if (agora - tempo_ultimo_rosto).total_seconds() < 1.0:
                rostos_detectados = ultimo_rosto
            else:
                rostos_detectados = []

        # Para cada rosto detectado.
        for rosto in rostos_detectados:
            embedding = rosto.embedding
            bbox = rosto.bbox.astype(int)
            top, left, bottom, right = bbox[1], bbox[0], bbox[3], bbox[2]

            # Compara com os rostos conhecidos.
            similaridades = [cosine_similarity(embedding, ref) for ref in rostos_conhecidos]
            melhor_id = int(np.argmax(similaridades)) if similaridades else -1
            melhor_sim = similaridades[melhor_id] if melhor_id != -1 else 0

            if melhor_sim > SIMILARITY_THRESHOLD:
                # Rosto reconhecido.
                info_base = infos_dos_rostos[melhor_id]
                nome_padronizado = info_base["nome"].strip().upper()
                dados = obter_dados_aluno_com_cache(nome_padronizado)
                nome = dados["nome"]
                turma = dados["turma"]
                texto_exibicao = f"{nome} ({turma})"
                cor = (0, 255, 0)

                tempo_espera = obter_tempo_espera()
                if nome in tempo_ultima_ocorrencia and (agora - tempo_ultima_ocorrencia[nome]) < timedelta(minutes=tempo_espera):
                    mensagem = f"⏳ {texto_exibicao} já registrado(a) recentemente! Ignorado..."
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
                # Rosto desconhecido.
                texto_exibicao = "Desconhecido"
                cor = (0, 0, 255)
                if (agora - tempo_ultimo_alerta_desconhecido) > timedelta(seconds=5):
                    socketio.emit('alerta', {
                        'mensagem': "⚠️ Rosto não reconhecido! Registro não realizado...",
                        'nome': texto_exibicao,
                        'tipo': "erro"
                    }, namespace='/')
                    tempo_ultimo_alerta_desconhecido = agora

            # Desenha a caixa e o nome no frame.
            cv2.rectangle(frame, (left, top), (right, bottom), cor, 2)
            meio_caixa = (left + right) // 2
            frame = desenhar_texto(frame, texto_exibicao, (meio_caixa, bottom + 10))

        # Codifica o frame final como imagem jpg para enviar ao navegador.
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')