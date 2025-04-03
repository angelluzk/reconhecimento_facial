import face_recognition as fr
import os
from datetime import datetime, timedelta
from database.connection import get_db_connection

# 🔹 Dicionário para armazenar o último registro de presença de cada aluno e evitar duplicação em curto intervalo.
ultimo_registro_por_aluno = {}

# 🔹 Tempo mínimo (em minutos) entre registros para o mesmo aluno.
TEMPO_ESPERA_MINUTOS = 10

def reconhece_face(url_foto):
    foto = fr.load_image_file(url_foto)
    rostos = fr.face_encodings(foto)
    return (True, rostos) if rostos else (False, [])

def get_rostos():
    rostos_conhecidos, nomes_dos_rostos = [], []
    pasta_fotos = os.path.join(os.path.abspath(os.path.dirname(__file__)), "fotos_alunos")
    
    for arquivo in os.listdir(pasta_fotos):
        if arquivo.lower().endswith(('png', 'jpg', 'jpeg')):
            caminho_imagem = os.path.join(pasta_fotos, arquivo)
            nome_aluno = os.path.splitext(arquivo)[0]
            sucesso, rostos = reconhece_face(caminho_imagem)
            if sucesso:
                rostos_conhecidos.append(rostos[0])
                nomes_dos_rostos.append(nome_aluno)
    
    return rostos_conhecidos, nomes_dos_rostos

def registrar_ocorrencia(nome_aluno):
    global ultimo_registro_por_aluno
    agora = datetime.now()
    limite_tempo = agora - timedelta(minutes=TEMPO_ESPERA_MINUTOS)

    # 🔹 Verifica se o aluno já foi registrado recentemente para evitar duplicação.
    if nome_aluno in ultimo_registro_por_aluno and ultimo_registro_por_aluno[nome_aluno] > limite_tempo:
        return  # Ignora se o último registro foi recente.

    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor(dictionary=True)
    
    # 🔹 Verifica se o aluno está cadastrado no banco.
    cursor.execute("SELECT id FROM alunos WHERE nome = %s", (nome_aluno,))
    aluno = cursor.fetchone()

    if not aluno:
        conn.close()
        return

    id_aluno = aluno['id']
    data_atual = agora.strftime('%Y-%m-%d')

    # 🔹 Verifica o último registro do aluno no dia atual.
    cursor.execute("""
        SELECT id, tipo_registro, data_hora 
        FROM registros_presenca 
        WHERE id_aluno = %s AND DATE(data_hora) = %s
        ORDER BY data_hora DESC LIMIT 1
    """, (id_aluno, data_atual))
    
    ultimo_registro = cursor.fetchone()
    
    if ultimo_registro:
        ultimo_horario = ultimo_registro['data_hora']
        if ultimo_horario >= limite_tempo:
            conn.close()
            return  # 🔹 Ignora o registro se for muito recente.

    # 🔹 Define o tipo de registro: Entrada se for o primeiro do dia, se não, Saída.
    if not ultimo_registro or ultimo_registro['tipo_registro'] == "saida":
        tipo_registro = "entrada"
    else:
        tipo_registro = "saida"

    # 🔹 Insere o novo registro no banco de dados.
    cursor.execute("""
        INSERT INTO registros_presenca (id_aluno, tipo_registro, data_hora)
        VALUES (%s, %s, %s)
    """, (id_aluno, tipo_registro, agora.strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    cursor.close()
    conn.close()

    # 🔹 Atualiza o último registro do aluno.
    ultimo_registro_por_aluno[nome_aluno] = agora
