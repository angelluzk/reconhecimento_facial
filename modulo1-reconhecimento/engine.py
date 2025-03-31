# Módulo responsável pelo processamento das imagens e registro de ocorrências no banco de dados.
import face_recognition as fr
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Garante que o python encontre o módulo database.connection corretamente.
from database.connection import get_db_connection

ultimo_registro_por_aluno = {} # Dicionário para armazenar a última vez que um aluno foi registrado.

#Função que carrega a imagem e tenta extrair as codificações faciais.
def reconhece_face(url_foto):
    foto = fr.load_image_file(url_foto)
    rostos = fr.face_encodings(foto)
    return (True, rostos) if rostos else (False, [])

# Função que lê as imagens dos alunos armazenadas e retorna os rostos reconhecidos.
def get_rostos():
    rostos_conhecidos = []
    nomes_dos_rostos = []
    pasta_fotos = os.path.join(os.path.dirname(__file__), "fotos_alunos")
    
    for arquivo in os.listdir(pasta_fotos):
        if arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            caminho_imagem = os.path.join(pasta_fotos, arquivo)
            nome_aluno = os.path.splitext(arquivo)[0]
            sucesso, rostos = reconhece_face(caminho_imagem)
            if sucesso:
                rostos_conhecidos.append(rostos[0])
                nomes_dos_rostos.append(nome_aluno)
    
    return rostos_conhecidos, nomes_dos_rostos

# Função que registra a entrada ou saída de um aluno no banco de dados.
def registrar_ocorrencia(nome_aluno):
    global ultimo_registro_por_aluno
    TEMPO_ESPERA = timedelta(seconds=10)
    agora = datetime.now()

    # Verifica se o aluno já foi registrado recentemente.
    if nome_aluno in ultimo_registro_por_aluno and (agora - ultimo_registro_por_aluno[nome_aluno]) < TEMPO_ESPERA:
        print(f"{nome_aluno} já foi registrado recentemente. Ignorando...")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM alunos WHERE nome = %s", (nome_aluno,))
    aluno = cursor.fetchone()
    if not aluno:
        print(f"Aluno '{nome_aluno}' não encontrado no banco de dados.")
        conn.close()
        return

    id_aluno = aluno['id']
    data_hora = agora.strftime('%Y-%m-%d %H:%M:%S')

    # Verifica o último registro para determinar se é entrada ou saída do aluno.
    cursor.execute("SELECT tipo_registro FROM registros_presenca WHERE id_aluno = %s ORDER BY data_hora DESC LIMIT 1", (id_aluno,))
    ultimo_registro = cursor.fetchone()
    tipo_registro = "entrada" if not ultimo_registro or ultimo_registro['tipo_registro'] == "saida" else "saida"

    cursor.execute("INSERT INTO registros_presenca (id_aluno, tipo_registro, data_hora) VALUES (%s, %s, %s)", (id_aluno, tipo_registro, data_hora))
    conn.commit()
    conn.close()

    ultimo_registro_por_aluno[nome_aluno] = agora
    print(f"{nome_aluno} registrou {tipo_registro}.")
    