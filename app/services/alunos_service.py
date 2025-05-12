import os
import io
import re
import unicodedata
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from PIL import Image
from app.database.connection import get_db_connection
from app.utils.caminhos import FOTOS_ALUNOS_DIR, EMBEDDINGS_DIR

try:
    import torch
    device = 0 if torch.cuda.is_available() else -1
except ImportError:
    device = -1

face_app = FaceAnalysis(name='buffalo_l')
face_app.prepare(ctx_id=device)

id_aluno_cache = {}


def nome_para_arquivo(nome):
    nome_sem_acentos = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII') 
    return re.sub(r'\W+', '_', nome_sem_acentos).strip('_')


def salvar_foto_no_disco(id_aluno, nome_arquivo, index, imagem_bytes):
    try:
        imagem = Image.open(io.BytesIO(imagem_bytes)).convert("RGB")

        np_img = np.array(imagem)
        np_img_bgr = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

        caminho_foto = os.path.join(FOTOS_ALUNOS_DIR, f"{id_aluno}_{nome_arquivo}_{index}.jpg")
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
    faces = face_app.get(img_rgb)
    if not faces:
        return None
    return faces[0].embedding

def processar_cadastro_web(nome, ano, turma_letra, turno, imagem_bytes, index):
    turno = (turno or '').strip()
    if not turno:
        turno = 'integral'

    turma = f"{ano} {turma_letra}"

    nome_formatado_bd = nome.strip()

    nome_arquivo = nome_para_arquivo(nome.strip()) 

    if not imagem_bytes:
        print("⚠️ Nenhuma imagem recebida.")
        return {"sucesso": False, "mensagem": "Imagem vazia recebida."}

    if index == 1:
        conexao = get_db_connection()
        if not conexao:
            print("❌ Falha ao conectar ao banco de dados.")
            return {"sucesso": False, "mensagem": "Erro ao conectar ao banco de dados."}

        cursor = conexao.cursor()
        try:
            cursor.execute("""
                INSERT INTO alunos (nome, foto, turno, turma)
                VALUES (%s, %s, %s, %s)
            """, (nome_formatado_bd, "", turno, turma))

            conexao.commit()
            id_aluno = cursor.lastrowid
            id_aluno_cache[nome_formatado_bd] = id_aluno
            print(f"✅ Aluno '{nome_formatado_bd}' cadastrado com ID {id_aluno}")

            caminho_foto, face_img = salvar_foto_no_disco(id_aluno, nome_arquivo, index, imagem_bytes)
            if caminho_foto:
                caminho_relativo_foto = os.path.relpath(caminho_foto, FOTOS_ALUNOS_DIR).replace("\\", "/")
                
                cursor.execute("""
                    UPDATE alunos SET foto = %s WHERE id = %s
                """, (caminho_relativo_foto, id_aluno))
                conexao.commit()
                print(f"🖼️ Foto registrada na tabela alunos: {caminho_relativo_foto}")

                cursor.execute("""
                    INSERT INTO fotos_alunos (id_aluno, foto_nome)
                    VALUES (%s, %s)
                """, (id_aluno, caminho_relativo_foto))
                conexao.commit()

        except Exception as e:
            print(f"❌ Erro ao salvar aluno: {e}")
            conexao.rollback()
            return {"sucesso": False, "mensagem": "Erro ao salvar aluno."}
        finally:
            cursor.close()
            conexao.close()
    else:
        id_aluno = id_aluno_cache.get(nome_formatado_bd)
        if not id_aluno:
            print(f"❌ ID não encontrado no cache para {nome_formatado_bd}.")
            return {"sucesso": False, "mensagem": "ID do aluno não encontrado."}

        try:
            imagem = Image.open(io.BytesIO(imagem_bytes)).convert("RGB")
            np_img = np.array(imagem)
            face_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"[ERRO] Erro ao converter imagem: {e}")
            return {"sucesso": False, "mensagem": "Erro ao processar imagem para embedding."}

    embedding = gerar_embedding(face_img)
    if embedding is not None:
        caminho_embedding = os.path.join(EMBEDDINGS_DIR, f"{id_aluno}_{nome_arquivo}_{index}.npy")
        np.save(caminho_embedding, embedding)
        print(f"\U0001F4BE Embedding {index} salvo em {caminho_embedding}")
    else:
        print(f"⚠️ Embedding não gerado para imagem {index}")

    return {"sucesso": True, "mensagem": f"Imagem {index} processada com sucesso!"}


def atualizar_aluno(id_aluno, nome, turno, ano, turma, foto_path=None):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            turma_completa = f"{ano} {turma}"

            if foto_path:
                if os.path.exists(foto_path):
                    cursor.execute(""" 
                        UPDATE alunos 
                        SET nome = %s, turno = %s, turma = %s, foto = %s 
                        WHERE id = %s
                    """, (nome, turno, turma_completa, foto_path, id_aluno))
                else:
                    return {"sucesso": False, "mensagem": "Foto não encontrada."}
            else:
                cursor.execute(""" 
                    UPDATE alunos 
                    SET nome = %s, turno = %s, turma = %s 
                    WHERE id = %s
                """, (nome, turno, turma_completa, id_aluno))

            conn.commit()
        return {"sucesso": True, "mensagem": "Aluno atualizado com sucesso!"}
    except Exception as e:
        print(f"[ERRO] Erro ao atualizar aluno: {e}")
        return {"sucesso": False, "mensagem": "Erro ao atualizar aluno."}

    finally:
        conn.close()


def excluir_aluno(id_aluno):
    try:
        conn = get_db_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                "DELETE FROM registros_presenca WHERE id_aluno = %s", (id_aluno,))
            conn.commit()
            cursor.execute("SELECT * FROM alunos WHERE id = %s", (id_aluno,))
            aluno = cursor.fetchone()
            if not aluno:
                return {"sucesso": False, "mensagem": "Aluno não encontrado."}

            cursor.execute(
                "SELECT foto_nome FROM fotos_alunos WHERE id_aluno = %s", (id_aluno,))
            fotos = cursor.fetchall()

            for foto in fotos:
                caminho_foto = os.path.join(
                    FOTOS_ALUNOS_DIR, foto['foto_nome'])
                print(f"Tentando remover a foto: {caminho_foto}")
                if os.path.exists(caminho_foto):
                    os.remove(caminho_foto)
                    print(f"🗑️ Foto removida: {caminho_foto}")
                else:
                    print(f"🚫 Foto não encontrada: {caminho_foto}")

            cursor.execute(
                "DELETE FROM fotos_alunos WHERE id_aluno = %s", (id_aluno,))
            conn.commit()

        for arq in os.listdir(EMBEDDINGS_DIR):
            if arq.startswith(f"{id_aluno}_") and arq.endswith(".npy"):
                caminho_arquivo = os.path.join(EMBEDDINGS_DIR, arq)
                print(f"Tentando remover o embedding: {caminho_arquivo}")
                if os.path.exists(caminho_arquivo):
                    os.remove(caminho_arquivo)
                    print(f"🗑️ Embedding removido: {caminho_arquivo}")
                else:
                    print(f"🚫 Embedding não encontrado: {caminho_arquivo}")

        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM alunos WHERE id = %s", (id_aluno,))
            conn.commit()

        return {"sucesso": True, "mensagem": "Aluno excluído com sucesso e arquivos removidos!"}

    except Exception as e:
        print(f"[ERRO] Erro ao excluir aluno: {e}")
        return {"sucesso": False, "mensagem": "Erro ao excluir aluno."}
    finally:
        conn.close()


def listar_alunos(turno=None, turma=None, nome=None, pagina=1, alunos_por_pagina=10):
    try:
        conn = get_db_connection()
        with conn.cursor(dictionary=True) as cursor:

            if pagina < 1:
                pagina = 1

            offset = (pagina - 1) * alunos_por_pagina

            query = "SELECT * FROM alunos WHERE 1=1"
            params = []

            if turno:
                query += " AND turno = %s"
                params.append(turno)
            if turma:
                query += " AND turma = %s"
                params.append(turma)
            if nome:
                query += " AND nome LIKE %s"
                params.append(f"%{nome}%")

            query += " LIMIT %s OFFSET %s"
            params.extend([alunos_por_pagina, offset])

            cursor.execute(query, params)
            alunos = cursor.fetchall()

            count_query = "SELECT COUNT(*) FROM alunos WHERE 1=1"
            count_params = []

            if turno:
                count_query += " AND turno = %s"
                count_params.append(turno)
            if turma:
                count_query += " AND turma = %s"
                count_params.append(turma)
            if nome:
                count_query += " AND nome LIKE %s"
                count_params.append(f"%{nome}%")

            cursor.execute(count_query, count_params)
            resultado = cursor.fetchone()
            total_alunos = list(resultado.values())[0] if resultado else 0

        return alunos, total_alunos
    except Exception as e:
        print(f"[ERRO] Erro ao listar alunos: {e}")
        return [], 0
    finally:
        if 'conn' in locals():
            conn.close()


def buscar_nome_e_turma_por_nome(nome_padronizado):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT nome, turma FROM alunos WHERE UPPER(TRIM(nome)) = %s", (nome_padronizado,))

        resultado = cursor.fetchone()

        cursor.close()
        conn.close()

        return resultado if resultado else {"nome": nome_padronizado, "turma": "Desconhecida"}
    except Exception as e:
        print(f"[ERRO] Erro ao buscar nome e turma: {e}")
        return {"nome": nome_padronizado, "turma": "Desconhecida"}