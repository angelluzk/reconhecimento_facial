import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from PIL import Image
from database.connection import get_db_connection
import io
import re
import unicodedata

try:
    import torch
    ctx_id = 0 if torch.cuda.is_available() else -1
except ImportError:
    ctx_id = -1

app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=ctx_id)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FOTOS_DIR = os.path.join(BASE_DIR, 'fotos_alunos')
EMBEDDINGS_DIR = os.path.join(BASE_DIR, 'embeddings_cache')
os.makedirs(FOTOS_DIR, exist_ok=True)
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

id_aluno_cache = {}

def nome_para_arquivo(nome):
    nome_sem_acentos = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'\W+', '_', nome_sem_acentos).strip('_')

def salvar_foto_no_disco(nome_arquivo, index, imagem_bytes):
    try:
        imagem = Image.open(io.BytesIO(imagem_bytes)).convert("RGB")

        np_img = np.array(imagem)
        np_img_bgr = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

        caminho_foto = os.path.join(FOTOS_DIR, f"{nome_arquivo}_{index}.jpg")
        print(f"[DEBUG] Salvando imagem em: {caminho_foto}")

        sucesso = cv2.imwrite(caminho_foto, np_img_bgr)

        if not sucesso:
            print(f"[ERRO] Falha ao salvar a imagem em {caminho_foto}")
        else:
            print(f"[INFO] Imagem salva com sucesso em {caminho_foto}")

        return caminho_foto, np_img_bgr

    except Exception as e:
        print(f"[ERRO] Exceção ao salvar imagem: {e}")
        return None, None

def gerar_embedding(face_img):
    img_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    faces = app.get(img_rgb)
    if not faces:
        return None
    return faces[0].embedding

def processar_cadastro_web(nome, turma, turno, imagem_bytes, index):
    turno = (turno or '').strip()
    if not turno:
        turno = 'integral'

    nome_formatado = nome.strip()
    nome_arquivo = nome_para_arquivo(nome_formatado)

    caminho_foto, face_img = salvar_foto_no_disco(nome_arquivo, index, imagem_bytes)
    embedding = gerar_embedding(face_img)

    if index == 1:
        caminho_relativo_foto = f"fotos_alunos/{os.path.basename(caminho_foto)}"

        conexao = get_db_connection()
        if not conexao:
            print("❌ Falha ao conectar ao banco de dados no cadastro.")
            return

        cursor = conexao.cursor()
        try:
            cursor.execute("""
                INSERT INTO alunos (nome, foto, turno, turma)
                VALUES (%s, %s, %s, %s)
            """, (nome_formatado, caminho_relativo_foto, turno, turma))
            conexao.commit()
            id_aluno = cursor.lastrowid
            id_aluno_cache[nome_formatado] = id_aluno
            print(f"✅ Aluno '{nome_formatado}' cadastrado no banco de dados com sucesso (ID: {id_aluno}).")
        except Exception as e:
            print(f"❌ Erro ao salvar aluno no banco de dados: {e}")
            conexao.rollback()
            return
        finally:
            cursor.close()
            conexao.close()
    else:
        id_aluno = id_aluno_cache.get(nome_formatado)

    if embedding is not None and id_aluno:
        caminho_embedding = os.path.join(EMBEDDINGS_DIR, f"{id_aluno}_{nome_arquivo}_{index}.npy")
        np.save(caminho_embedding, embedding)
        print(f"\U0001F4BE Embedding {index} salvo em {caminho_embedding}")
    else:
        print(f"⚠️ Embedding não gerado para imagem {index}")