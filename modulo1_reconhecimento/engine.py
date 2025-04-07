import cv2
import os
import numpy as np
from datetime import datetime, timedelta
from insightface.app import FaceAnalysis
from database.connection import get_db_connection

try:
    import torch
    ctx_id = 0 if torch.cuda.is_available() else -1
except ImportError:
    ctx_id = -1

face_app = FaceAnalysis(name='buffalo_l')
face_app.prepare(ctx_id=ctx_id)

TEMPO_ESPERA_MINUTOS = 10

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
    rostos_conhecidos, nomes_dos_rostos = [], []
    pasta_fotos = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), "fotos_alunos")

    for arquivo in os.listdir(pasta_fotos):
        if arquivo.lower().endswith(('png', 'jpg', 'jpeg')):
            caminho_imagem = os.path.join(pasta_fotos, arquivo)
            nome_aluno = os.path.splitext(arquivo)[0].replace('_', ' ')
            sucesso, rostos = reconhece_face(caminho_imagem)
            if sucesso and rostos:
                rostos_conhecidos.append(rostos[0])
                nomes_dos_rostos.append(nome_aluno)
            else:
                print(f"[AVISO] Rosto não detectado em: {arquivo}")

    return rostos_conhecidos, nomes_dos_rostos

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def verificar_identidade(embedding_desconhecido, conhecidos, nomes, threshold=0.5):
    similaridades = [cosine_similarity(
        embedding_desconhecido, emb) for emb in conhecidos]
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

    conn = get_db_connection()
    if not conn:
        return None, "❌ Erro ao conectar ao banco de dados"

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, turma FROM alunos WHERE nome = %s", (nome_aluno,))
    aluno = cursor.fetchone()

    if not aluno:
        conn.close()
        return None, "⚠️ Aluno não encontrado no banco de dados"

    id_aluno = aluno['id']
    turma = aluno['turma']

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
            conn.close()
            return None, "⏳ Registro ignorado (último registro há menos de 10 minutos)"

    tipo_registro = "entrada" if not ultimo_registro or ultimo_registro[
        'tipo_registro'] == "saida" else "saida"

    cursor.execute("""
        INSERT INTO registros_presenca (id_aluno, turma, tipo_registro, data_hora)
        VALUES (%s, %s, %s, %s)
    """, (id_aluno, turma, tipo_registro, agora.strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    cursor.close()
    conn.close()

    return tipo_registro, f"✅ Aluno {nome_aluno} ({turma}) reconhecido e {tipo_registro} registrada!"