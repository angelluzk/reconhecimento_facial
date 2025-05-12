import os
import re
import cv2
import unicodedata
import numpy as np
import logging
from datetime import datetime, timedelta
from insightface.app import FaceAnalysis
from app.database.connection import get_db_connection
from app.utils.caminhos import EMBEDDINGS_DIR

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s')

try:
    import torch
    device = 0 if torch.cuda.is_available() else -1
except ImportError:
    device = -1

face_app = FaceAnalysis(name='buffalo_l')
face_app.prepare(ctx_id=device)

def verificar_conexao_banco():
    conn = get_db_connection()
    if not conn:
        logging.error("Erro ao conectar ao banco de dados.")
        return None
    return conn

def carregar_face_model():
    return face_app

def formatar_nome_turma(nome, turma):
    nome_formatado = unicodedata.normalize('NFC', nome)
    turma_formatada = unicodedata.normalize('NFC', turma)
    turma_formatada = turma_formatada.replace("O", "º").replace("o", "º")

    return f"{nome_formatado} ({turma_formatada})"

def obter_tempo_espera():
    try:
        conn = verificar_conexao_banco()
        if not conn:
            return 10
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT valor, tipo FROM configuracoes WHERE nome_configuracao = 'tempo_espera'")
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        if resultado:
            valor = int(resultado['valor'])
            return valor * 60 if resultado['tipo'] == 'horas' else valor
    except Exception as e:
        logging.error(f"Erro ao buscar tempo de espera: {e}")
    return 10

def nome_para_arquivo(nome):
    nome_sem_acentos = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'\W+', '_', nome_sem_acentos).strip('_')

def ler_imagem_cv2(caminho):
    try:
        with open(caminho, 'rb') as f:
            return cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
    except Exception as e:
        logging.error(f"Falha ao ler imagem: {caminho} -> {e}")
        return None

def carregar_embedding(arquivo):
    try:
        embedding = np.load(arquivo)
        if embedding.ndim != 1:
            raise ValueError(f"Arquivo {arquivo} não contém um vetor de embedding válido.")
        return embedding
    except Exception as e:
        logging.error(f"Erro ao carregar o embedding {arquivo}: {e}")
        return None

def get_rostos():
    rostos_conhecidos, infos_dos_rostos = [], []
    if not os.path.exists(EMBEDDINGS_DIR):
        logging.warning("Diretório de embeddings não encontrado.")
        return [], []

    logging.info(f"Iniciando o carregamento dos embeddings do diretório {EMBEDDINGS_DIR}...")

    alunos_db = {}
    
    for arquivo in os.listdir(EMBEDDINGS_DIR):
        if arquivo.endswith('.npy'):
            try:
                caminho = os.path.join(EMBEDDINGS_DIR, arquivo)
                embedding = carregar_embedding(caminho)
                if embedding is None:
                    continue

                nome_arquivo = os.path.splitext(arquivo)[0]
                partes = nome_arquivo.split('_')
                if partes and partes[0].isdigit():
                    id_aluno = int(partes[0])

                    if id_aluno not in alunos_db:
                        info_aluno = obter_info_por_id(id_aluno)
                        if info_aluno:
                            alunos_db[id_aluno] = info_aluno
                    else:
                        info_aluno = alunos_db[id_aluno]
                    
                    if info_aluno:
                        norm = np.linalg.norm(embedding)
                        if norm > 0:
                            rostos_conhecidos.append(embedding / norm)
                            infos_dos_rostos.append(info_aluno)
                else:
                    logging.warning(f"Arquivo {arquivo} não segue o formato esperado (id_aluno_nome).")
            except Exception as e:
                logging.error(f"Erro ao carregar {arquivo}: {e}")
    
    logging.info(f"Carregamento de embeddings concluído. {len(rostos_conhecidos)} rostos conhecidos carregados.")
    return rostos_conhecidos, infos_dos_rostos

def cosine_similarity(a, b):
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0
    return np.dot(a, b) / (norm_a * norm_b)

def registrar_ocorrencia(nome_aluno):
    agora = datetime.now()
    data_atual = agora.strftime('%Y-%m-%d')
    nome_aluno = nome_aluno.strip().upper()

    conn = verificar_conexao_banco()
    if not conn:
        return None, "❌ Erro ao conectar ao banco de dados."

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, turma FROM alunos WHERE nome = %s", (nome_aluno,))
        aluno = cursor.fetchone()

        if not aluno:
            return None, "⚠️ Aluno não encontrado no banco de dados."

        id_aluno = aluno['id']
        turma = aluno['turma']

        cursor.execute(""" 
            SELECT tipo_registro, data_hora FROM registros_presenca
            WHERE id_aluno = %s AND DATE(data_hora) = %s
            ORDER BY data_hora DESC LIMIT 1
        """, (id_aluno, data_atual))

        ultimo_registro = cursor.fetchone()

        tempo_espera = obter_tempo_espera()

        if ultimo_registro:
            tempo_ultimo = ultimo_registro['data_hora']
            if tempo_ultimo > (agora - timedelta(minutes=tempo_espera)):
                return None, f"⏳ Registro ignorado (último há menos de {tempo_espera} min)."

        tipo_registro = "entrada" if not ultimo_registro or ultimo_registro['tipo_registro'] == "saida" else "saida"

        cursor.execute(""" 
            INSERT INTO registros_presenca (id_aluno, turma, tipo_registro, data_hora)
            VALUES (%s, %s, %s, %s)
        """, (id_aluno, turma, tipo_registro, agora.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()

        return tipo_registro, f"✅ Aluno {nome_aluno} ({turma}) reconhecido e {tipo_registro} registrada!"
    except Exception as e:
        logging.error(f"Erro ao registrar ocorrência: {e}")
        return None, "❌ Erro ao registrar a ocorrência."
    finally:
        cursor.close()
        conn.close()

def obter_info_por_id(id_aluno):
    try:
        conn = verificar_conexao_banco()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alunos WHERE id = %s", (id_aluno,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        return resultado
    except Exception as e:
        logging.error(f"Erro ao buscar aluno {id_aluno}: {e}")
        return None