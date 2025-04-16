import cv2
import os
import numpy as np
from datetime import datetime, timedelta
from insightface.app import FaceAnalysis
from database.connection import get_db_connection
import unicodedata
import re

try:
    import torch
    if hasattr(torch, 'cuda') and torch.cuda.is_available():
        device = 0
    else:
        device = -1
except ImportError:
    device = -1

face_app = FaceAnalysis(name='buffalo_l')
face_app.prepare(ctx_id=device)

TEMPO_ESPERA_MINUTOS = 10

def nome_para_arquivo(nome):
    nome_sem_acentos = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'\W+', '_', nome_sem_acentos).strip('_')

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

def reconhece_face(url_foto):
    imagem = ler_imagem_unicode(url_foto)
    if imagem is None:
        return False, []
    rostos = face_app.get(imagem)
    rostos = sorted(rostos, key=lambda r: r.bbox[2] * r.bbox[3], reverse=True)
    return (True, [r.embedding for r in rostos]) if rostos else (False, [])

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

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

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

    while cursor.nextset():
        pass

    cursor.execute("""
        SELECT id, tipo_registro, data_hora 
        FROM registros_presenca 
        WHERE id_aluno = %s AND DATE(data_hora) = %s
        ORDER BY data_hora DESC LIMIT 1
    """, (id_aluno, data_atual))

    ultimo_registro = cursor.fetchone()

    if ultimo_registro:
        tempo_ultimo = ultimo_registro['data_hora']
        if tempo_ultimo > (agora - timedelta(minutes=TEMPO_ESPERA_MINUTOS)):
            cursor.close()
            conn.close()
            return None, "⏳ Registro ignorado (último registro há menos de 10 minutos)."

    tipo_registro = "entrada" if not ultimo_registro or ultimo_registro['tipo_registro'] == "saida" else "saida"

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

def carregar_face_model():
    return face_app

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