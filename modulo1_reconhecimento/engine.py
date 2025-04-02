import face_recognition as fr
import os
from datetime import datetime, timedelta
from database.connection import get_db_connection

ultimo_registro_por_aluno = {} # Dicionário para armazenar o último registro de presença de cada aluno e evitar registros duplicados em curto intervalo.

def reconhece_face(url_foto):
    foto = fr.load_image_file(url_foto)
    rostos = fr.face_encodings(foto)
    return (True, rostos) if rostos else (False, [])

def get_rostos():
    rostos_conhecidos, nomes_dos_rostos = [], []
    pasta_fotos = os.path.join(os.path.abspath(os.path.dirname(__file__)), "fotos_alunos")
    
    # Percorre todos os arquivos dentro da pasta de fotos.
    for arquivo in os.listdir(pasta_fotos):
        if arquivo.lower().endswith(('png', 'jpg', 'jpeg')):
            caminho_imagem = os.path.join(pasta_fotos, arquivo)
            nome_aluno = os.path.splitext(arquivo)[0]
            sucesso, rostos = reconhece_face(caminho_imagem)
            if sucesso:
                rostos_conhecidos.append(rostos[0])
                nomes_dos_rostos.append(nome_aluno)
    
    return rostos_conhecidos, nomes_dos_rostos

# Registra a entrada ou saída de um aluno no banco de dados, evitando múltiplos registros em curto intervalo de tempo.
def registrar_ocorrencia(nome_aluno):
    global ultimo_registro_por_aluno
    TEMPO_ESPERA = timedelta(seconds=10)
    agora = datetime.now()

    if nome_aluno in ultimo_registro_por_aluno and (agora - ultimo_registro_por_aluno[nome_aluno]) < TEMPO_ESPERA:
        return

    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM alunos WHERE nome = %s", (nome_aluno,))
    aluno = cursor.fetchone()

    if not aluno:
        conn.close()
        return

    id_aluno = aluno['id']
    cursor.execute("SELECT tipo_registro FROM registros_presenca WHERE id_aluno = %s ORDER BY data_hora DESC LIMIT 1", (id_aluno,))
    ultimo_registro = cursor.fetchone()
    tipo_registro = "entrada" if not ultimo_registro or ultimo_registro['tipo_registro'] == "saida" else "saida"

    cursor.execute("INSERT INTO registros_presenca (id_aluno, tipo_registro, data_hora) VALUES (%s, %s, %s)",
                   (id_aluno, tipo_registro, agora.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

    ultimo_registro_por_aluno[nome_aluno] = agora