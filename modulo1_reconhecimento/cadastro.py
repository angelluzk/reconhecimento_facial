# Importações necessárias para manipulação de arquivos, imagens, embeddings faciais e banco de dados.
import os # Para lidar com pastas e arquivos no sistema operacional.
import cv2 # Biblioteca para trabalhar com imagens e vídeos.
import numpy as np  # Biblioteca para trabalhar com arrays (listas de números).
from insightface.app import FaceAnalysis # Biblioteca para reconhecer rostos e extrair informações.
from PIL import Image # Biblioteca para abrir e converter imagens.
from database.connection import get_db_connection
import io  # Usada para tratar arquivos como se fossem objetos em memória.
import re # Expressões regulares, usada aqui para limpar texto.
import unicodedata # Usada para remover acentos de letras (ex: "é" vira "e").

# Aqui tenta importar o torch (do PyTorch) e verificar se há uma placa de vídeo (GPU) disponível.
try:
    import torch
    ctx_id = 0 if torch.cuda.is_available() else -1 # Se tiver GPU, usa ela (ctx_id = 0), senão usa CPU (ctx_id = -1).
except ImportError:
    ctx_id = -1 # Se o torch nem estiver instalado, usa a CPU mesmo.

# Cria um "analisador facial", que é um objeto capaz de detectar rostos e gerar vetores únicos (embeddings).
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=ctx_id)

# Cria caminhos para armazenar as fotos e os arquivos com embeddings.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FOTOS_DIR = os.path.join(BASE_DIR, 'fotos_alunos')
EMBEDDINGS_DIR = os.path.join(BASE_DIR, 'embeddings_cache')

# Garante que as pastas existam! Se não existir, elas são criadas.
os.makedirs(FOTOS_DIR, exist_ok=True)
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

id_aluno_cache = {} # Dicionário para guardar o ID do aluno logo depois que ele é criado no banco. Assim evita consultar o banco toda hora.

# Essa função transforma um nome como "João da Silva!" em "Joao_da_Silva".
def nome_para_arquivo(nome):
    nome_sem_acentos = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII') # Remove acentos.
    return re.sub(r'\W+', '_', nome_sem_acentos).strip('_') # Substitui tudo que não for letra ou número por "_".

# Essa função salva a imagem que recebemos no formato de bytes dentro do disco.
def salvar_foto_no_disco(id_aluno, nome_arquivo, index, imagem_bytes):
    try:
        imagem = Image.open(io.BytesIO(imagem_bytes)).convert("RGB") # Abre a imagem e converte para RGB (cores normais).

        np_img = np.array(imagem)# Converte imagem para um array de números (pixels).
        np_img_bgr = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)  # Converte para BGR (formato que o OpenCV usa).

        # Define o nome do arquivo com base no ID do aluno e no número da imagem.
        caminho_foto = os.path.join(FOTOS_DIR, f"{id_aluno}_{nome_arquivo}_{index}.jpg")
        print(f"[DEBUG] Salvando imagem em: {caminho_foto}")

        sucesso = cv2.imwrite(caminho_foto, np_img_bgr)# Salva a imagem no disco.

        if not sucesso:
            print(f"[ERRO] Falha ao salvar a imagem em {caminho_foto}")
        else:
            print(f"[INFO] Imagem salva com sucesso em {caminho_foto}")

        return caminho_foto, np_img_bgr # Retorna o caminho da imagem salva e a imagem como array.

    except Exception as e:
        print(f"[ERRO] Exceção ao salvar imagem: {e}")
        return None, None

# Essa função gera o "embedding", ou seja, um vetor numérico que representa o rosto da pessoa.
def gerar_embedding(face_img):
    img_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB) # Converte para RGB para usar no InsightFace.
    faces = app.get(img_rgb)  # Detecta rostos na imagem.
    if not faces:
        return None # Se não achou nenhum rosto, retorna None.
    return faces[0].embedding # Retorna o vetor do primeiro rosto encontrado.

# Essa é a função principal que é chamada quando cadastramos um aluno pelo sistema.
def processar_cadastro_web(nome, ano, turma_letra, turno, imagem_bytes, index):
    turno = (turno or '').strip()
    if not turno:
        turno = 'integral'

    turma = f"{ano} {turma_letra}"
    nome_formatado = nome.strip().upper()
    nome_arquivo = nome_para_arquivo(nome_formatado)

    if not imagem_bytes:
        print("⚠️ Nenhuma imagem recebida.")
        return {"sucesso": False, "mensagem": "Imagem vazia recebida."}

    # Se for a primeira imagem, cria o aluno, salva uma única foto
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
            """, (nome_formatado, "", turno, turma))  # A foto ainda será vazia, vamos atualizar depois.
            conexao.commit()
            id_aluno = cursor.lastrowid
            id_aluno_cache[nome_formatado] = id_aluno
            print(f"✅ Aluno '{nome_formatado}' cadastrado com ID {id_aluno}")

            # Salva a imagem no disco.
            caminho_foto, face_img = salvar_foto_no_disco(id_aluno, nome_arquivo, index, imagem_bytes)
            if caminho_foto:
                caminho_relativo_foto = os.path.relpath(caminho_foto, FOTOS_DIR).replace("\\", "/")
                
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
        # Se for qualquer outra imagem (index > 1), só gera o embedding, sem salvar a imagem
        id_aluno = id_aluno_cache.get(nome_formatado)
        if not id_aluno:
            print(f"❌ ID não encontrado no cache para {nome_formatado}.")
            return {"sucesso": False, "mensagem": "ID do aluno não encontrado."}

        # Converte a imagem apenas para gerar o embedding
        try:
            imagem = Image.open(io.BytesIO(imagem_bytes)).convert("RGB")
            np_img = np.array(imagem)
            face_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"[ERRO] Erro ao converter imagem: {e}")
            return {"sucesso": False, "mensagem": "Erro ao processar imagem para embedding."}

    # Gera o embedding da imagem
    embedding = gerar_embedding(face_img)
    if embedding is not None:
        caminho_embedding = os.path.join(EMBEDDINGS_DIR, f"{id_aluno}_{nome_arquivo}_{index}.npy")
        np.save(caminho_embedding, embedding)
        print(f"\U0001F4BE Embedding {index} salvo em {caminho_embedding}")
    else:
        print(f"⚠️ Embedding não gerado para imagem {index}")

    return {"sucesso": True, "mensagem": f"Imagem {index} processada com sucesso!"}
