#Este módulo contém a lógica central para o reconhecimento e registro de presenças de alunos através de reconhecimento facial.

import cv2 # Para processamento de imagem.
import os # Para lidar com arquivos e diretórios.
import numpy as np # Para operações matemáticas e com vetores.
from datetime import datetime, timedelta # Para manipulação de datas e tempo.
from insightface.app import FaceAnalysis # Biblioteca de reconhecimento facial.
from database.connection import get_db_connection
import unicodedata # Para remover acentos.
import re # Para tratar strings com expressões regulares.

# Detecta se há suporte a CUDA (GPU), caso contrário usa CPU.
try:
    import torch
    if hasattr(torch, 'cuda') and torch.cuda.is_available():
        device = 0 # GPU.
    else:
        device = -1 # CPU.
except ImportError:
    device = -1 # CPU, se torch não estiver instalado.

# Inicializa o modelo facial com o modelo 'buffalo_l'.
face_app = FaceAnalysis(name='buffalo_l')
face_app.prepare(ctx_id=device) # Prepara o modelo com o dispositivo definido.

# Controle de detecção de frames.
frame_counter = 0
frame_interval = 3 # Frequência com que os rostos são detectados (a cada 3 frames).

#Função que busca no banco o tempo de espera entre registros do mesmo aluno. Pode estar configurado em minutos ou horas.
def obter_tempo_espera():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT valor, tipo FROM configuracoes WHERE nome_configuracao = 'tempo_espera'")
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        if resultado:
            valor = int(resultado['valor'])
            tipo = resultado['tipo']
            if tipo == 'horas':
                return valor * 60
            elif tipo == 'minutos':
                return valor
        return 10
    except Exception as e:
        print(f"[ERRO] Erro ao buscar tempo de espera: {e}")
        return 10

# Função que converte o nome de um aluno em um nome de arquivo seguro (sem acentos e com underscores).
def nome_para_arquivo(nome):
    nome_sem_acentos = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'\W+', '_', nome_sem_acentos).strip('_')

# Função que lê uma imagem a partir de um caminho que pode conter caracteres especiais (Unicode).
def ler_imagem_unicode(caminho):
    try:
        with open(caminho, 'rb') as f:
            bytes = bytearray(f.read())
            np_bytes = np.asarray(bytes, dtype=np.uint8)
            imagem = cv2.imdecode(np_bytes, cv2.IMREAD_COLOR)
            return imagem
    except Exception as e:
        print(f"[ERRO] Falha ao ler imagem: {caminho} -> {e}")
        return None

#Função que reconhece rostos em uma imagem a partir de seu caminho. Retorna os embeddings (representações vetoriais dos rostos).
def reconhece_face(url_foto):
    global frame_counter
    imagem = ler_imagem_unicode(url_foto)
    if imagem is None:
        return False, []

    if frame_counter % frame_interval == 0:
        rostos = face_app.get(imagem)
        rostos = sorted(rostos, key=lambda r: r.bbox[2] * r.bbox[3], reverse=True)
    else:
        rostos = []

    frame_counter += 1

    return (True, [r.embedding for r in rostos]) if rostos else (False, [])

#Função que carrega os rostos (embeddings) conhecidos salvos em arquivos .npy. Cada embedding é associado ao ID do aluno e suas informações.
def get_rostos():
    embeddings_dir = os.path.join(os.path.dirname(__file__), 'embeddings_cache')
    rostos_conhecidos = []
    infos_dos_rostos = []

    if not os.path.exists(embeddings_dir):
        print("[AVISO] Diretório de embeddings não encontrado.")
        return [], []

    for arquivo in os.listdir(embeddings_dir):
        if arquivo.endswith('.npy'):
            try:
                caminho = os.path.join(embeddings_dir, arquivo)
                embedding = np.load(caminho)
                nome_arquivo = os.path.splitext(arquivo)[0]
                partes = nome_arquivo.split('_')
                if partes and partes[0].isdigit():
                    id_aluno = int(partes[0])
                    info = obter_info_por_id(id_aluno)
                    if info:
                        rostos_conhecidos.append(embedding)
                        infos_dos_rostos.append(info)
            except Exception as e:
                print(f"[ERRO] Falha ao carregar embedding {arquivo}: {e}")

    print(f"[INFO] {len(rostos_conhecidos)} embeddings carregados do cache")
    return rostos_conhecidos, infos_dos_rostos

# Função que busca no banco o nome de um aluno a partir do seu ID.
def obter_nome_por_id(id_aluno):
    try:
        conn = get_db_connection()
        if not conn:
            print(f"[ERRO] Sem conexão com o banco de dados.")
            return None
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM alunos WHERE id = %s", (id_aluno,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        return resultado[0] if resultado else None
    except Exception as e:
        print(f"[ERRO] Erro ao buscar nome do(a) aluno(a) {id_aluno}: {e}")
        return None

# Função que calcula a similaridade de cosseno entre dois vetores (embeddings).
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

#Função que verifica se um embedding desconhecido corresponde a algum conhecido com base no limiar de similaridade.
def verificar_identidade(embedding_desconhecido, conhecidos, nomes, threshold=0.5):
    similaridades = [cosine_similarity(embedding_desconhecido, emb) for emb in conhecidos]
    if not similaridades:
        return None
    idx_mais_proximo = np.argmax(similaridades)
    if similaridades[idx_mais_proximo] >= threshold:
        print(f"[INFO] Similaridade: {similaridades[idx_mais_proximo]:.4f}")
        return nomes[idx_mais_proximo]
    print(f"[INFO] Similaridade abaixo do threshold: {max(similaridades):.4f}")
    return None

# Função que registra uma entrada ou saída do aluno no banco de dados, considerando o tempo de espera mínimo.
def registrar_ocorrencia(nome_aluno):
    agora = datetime.now()
    data_atual = agora.strftime('%Y-%m-%d')

    nome_aluno = nome_aluno.strip().upper()

    conn = get_db_connection()
    if not conn:
        return None, "❌ Erro ao conectar ao banco de dados."

    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, turma FROM alunos WHERE nome = %s", (nome_aluno,))
    aluno = cursor.fetchone()

    if not aluno:
        cursor.close()
        conn.close()
        return None, "⚠️ Aluno(a) não encontrado(a) no banco de dados."

    id_aluno = aluno['id']
    turma = aluno['turma']

    # Garante que não há resultados pendentes anteriores.
    while cursor.nextset():
        pass

    cursor.execute("""
        SELECT id, tipo_registro, data_hora 
        FROM registros_presenca 
        WHERE id_aluno = %s AND DATE(data_hora) = %s
        ORDER BY data_hora DESC LIMIT 1
    """, (id_aluno, data_atual))

    ultimo_registro = cursor.fetchone()

    tempo_espera_minutos = obter_tempo_espera()

    if ultimo_registro:
        tempo_ultimo = ultimo_registro['data_hora']
        if tempo_ultimo > (agora - timedelta(minutes=tempo_espera_minutos)):
            cursor.close()
            conn.close()
            return None, f"⏳ Registro ignorado (último registro há menos de {tempo_espera_minutos} minutos)."

    # Alterna entre entrada e saída.
    tipo_registro = "entrada" if not ultimo_registro or ultimo_registro['tipo_registro'] == "saida" else "saida"

    # Limpa possíveis resultados pendentes.
    while cursor.nextset():
        pass

    cursor.execute("""
        INSERT INTO registros_presenca (id_aluno, turma, tipo_registro, data_hora)
        VALUES (%s, %s, %s, %s)
    """, (id_aluno, turma, tipo_registro, agora.strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    cursor.close()
    conn.close()

    return tipo_registro, f"✅ Aluno(a) {nome_aluno} ({turma}) reconhecido(a) e {tipo_registro} registrada!"

# Função que retorna o modelo de análise facial carregado.
def carregar_face_model():
    return face_app

# Função que busca todas as informações do aluno pelo ID
def obter_info_por_id(id_aluno):
    try:
        conn = get_db_connection()
        if not conn:
            print(f"[ERRO] Sem conexão com o banco de dados.")
            return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alunos WHERE id = %s", (id_aluno,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        return resultado
    except Exception as e:
        print(f"[ERRO] Erro ao buscar informação do aluno(a) {id_aluno}: {e}")
        return None