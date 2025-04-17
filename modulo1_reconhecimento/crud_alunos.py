# Este módulo cuida das operações de CRUD relacionadas aos alunos. Aqui temos funções para atualizar, excluir e listar alunos, além de gerenciar as fotos e embeddings relacionados.

import os
from database.connection import get_db_connection
from datetime import datetime, timedelta
import threading
import time

cache_dados_aluno = {} # Cache temporário para nome e turma.

# Caminho onde ficam salvas as fotos dos alunos.
FOTOS_DIR = os.path.join(os.path.dirname(__file__), 'fotos_alunos')
# Caminho onde ficam salvos os arquivos de embeddings (vetores de rosto).
EMBEDDINGS_DIR = os.path.join(os.path.dirname(__file__), 'embeddings_cache')

# Função que garante que os diretórios de fotos e embeddings existam.
def garantir_diretorios():
    if not os.path.exists(FOTOS_DIR):
        os.makedirs(FOTOS_DIR)
    if not os.path.exists(EMBEDDINGS_DIR):
        os.makedirs(EMBEDDINGS_DIR)

garantir_diretorios() # Cria os diretórios assim que o arquivo for importado ou executado.

# Função que atualiza os dados de um aluno(a) no banco de dados.
def atualizar_aluno(id_aluno, nome, turno, turma, foto_path=None):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if foto_path:
                # Atualiza tudo, inclusive a foto.
                cursor.execute(""" 
                    UPDATE alunos 
                    SET nome = %s, turno = %s, turma = %s, foto = %s 
                    WHERE id = %s
                """, (nome, turno, turma, foto_path, id_aluno))
            else:
                # Atualiza apenas os dados, sem alterar a foto.
                cursor.execute("""
                    UPDATE alunos 
                    SET nome = %s, turno = %s, turma = %s 
                    WHERE id = %s
                """, (nome, turno, turma, id_aluno))

            conn.commit()
        return {"sucesso": True, "mensagem": "Aluno(a) atualizado(a) com sucesso!"}
    except Exception as e:
        print(f"[ERRO] Erro ao atualizar aluno(a): {e}")
        return {"sucesso": False, "mensagem": "Erro ao atualizar aluno(a)."}

    finally:
        conn.close()

# Função que exclui um aluno(a) do banco de dados, suas fotos e seus arquivos de embeddings.
def excluir_aluno(id_aluno):
    try:
        conn = get_db_connection()
        with conn.cursor(dictionary=True) as cursor:
            # Primeiro, remove os registros de presença do aluno(a).
            cursor.execute("DELETE FROM registros_presenca WHERE id_aluno = %s", (id_aluno,))
            conn.commit()
            # Busca os dados do aluno(a) para confirmar se ele existe.
            cursor.execute("SELECT * FROM alunos WHERE id = %s", (id_aluno,))
            aluno = cursor.fetchone()
            if not aluno:
                return {"sucesso": False, "mensagem": "Aluno(a) não encontrado(a)."}
            # Busca todas as fotos cadastradas desse aluno(a).
            cursor.execute("SELECT foto_nome FROM fotos_alunos WHERE id_aluno = %s", (id_aluno,))
            fotos = cursor.fetchall()

            # Tenta apagar cada uma das fotos do diretório.
            for foto in fotos:
                caminho_foto = os.path.join(FOTOS_DIR, foto['foto_nome'])
                print(f"Tentando remover a foto: {caminho_foto}")
                if os.path.exists(caminho_foto):
                    os.remove(caminho_foto)
                    print(f"🗑️ Foto removida: {caminho_foto}")
                else:
                    print(f"🚫 Foto não encontrada: {caminho_foto}")

            # Remove as entradas da tabela fotos_alunos no banco de dados.
            cursor.execute("DELETE FROM fotos_alunos WHERE id_aluno = %s", (id_aluno,))
            conn.commit()
        
        # Agora remove todos os arquivos de embeddings relacionados ao aluno(a).
        for arq in os.listdir(EMBEDDINGS_DIR):
            if arq.startswith(f"{id_aluno}_") and arq.endswith(".npy"):
                caminho_arquivo = os.path.join(EMBEDDINGS_DIR, arq)
                print(f"Tentando remover o embedding: {caminho_arquivo}")
                if os.path.exists(caminho_arquivo):
                    os.remove(caminho_arquivo)
                    print(f"🗑️ Embedding removido: {caminho_arquivo}")
                else:
                    print(f"🚫 Embedding não encontrado: {caminho_arquivo}")
        
        # Por fim, apaga o próprio aluno(a) da tabela alunos.
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM alunos WHERE id = %s", (id_aluno,))
            conn.commit()

        return {"sucesso": True, "mensagem": "Aluno(a) excluído(a) com sucesso e arquivos removidos!"}

    except Exception as e:
        print(f"[ERRO] Erro ao excluir aluno(a): {e}")
        return {"sucesso": False, "mensagem": "Erro ao excluir aluno(a)."}

    finally:
        conn.close()

# Função que retorna uma lista com todos os alunos cadastrados.
def listar_alunos():
    try:
        conn = get_db_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM alunos")
            alunos = cursor.fetchall()

        return alunos
    except Exception as e:
        print(f"[ERRO] Erro ao listar alunos: {e}")
        return []
    finally:
        conn.close()

# Função que busca no banco de dados o nome e a turma do aluno(a), com base no nome padronizado (maiúsculo e sem espaços).
def buscar_nome_e_turma_por_nome(nome_padronizado):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT nome, turma FROM alunos WHERE UPPER(TRIM(nome)) = %s", (nome_padronizado,))
    resultado = cursor.fetchone()

    cursor.close()
    conn.close()

    return resultado if resultado else {"nome": nome_padronizado, "turma": "Desconhecida"}

# Função que obtém o nome e turma do aluno(a) com o cache de 10 segundos para evitar sobrecarga no banco de dados.
def obter_dados_aluno_com_cache(nome_padronizado):
    agora = datetime.now()

    if nome_padronizado in cache_dados_aluno:
        dados, expira_em = cache_dados_aluno[nome_padronizado]
        if agora < expira_em:
            return dados

    dados = buscar_nome_e_turma_por_nome(nome_padronizado)
    cache_dados_aluno[nome_padronizado] = (dados, agora + timedelta(seconds=10))

    return dados

# Função que limpa os dados expirados do cache a cada 5 segundos.
def limpar_cache_periodicamente():
    while True:
        agora = datetime.now()
        expirados = [nome for nome, (_, expira_em) in cache_dados_aluno.items() if agora > expira_em]

        for nome in expirados:
            del cache_dados_aluno[nome]

        time.sleep(5)

# Inicia o processo de limpeza automática do cache.
threading.Thread(target=limpar_cache_periodicamente, daemon=True).start()