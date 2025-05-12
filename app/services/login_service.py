from werkzeug.security import generate_password_hash, check_password_hash
from app.database.connection import get_db_connection


def login_usuario(email, senha):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    usuario = cursor.fetchone()

    if usuario:
        if check_password_hash(usuario['senha'], senha):
            return usuario
    return None


def cadastrar_usuario(nome, email, senha, is_admin=False):
    conn = get_db_connection()
    if conn is None:
        print("Erro: Falha ao conectar no banco de dados.")
        return False

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    if cursor.fetchone():
        return False

    senha_hash = generate_password_hash(senha)
    cursor.execute("INSERT INTO usuarios (nome, email, senha, is_admin) VALUES (%s, %s, %s, %s)",
                   (nome, email, senha_hash, is_admin))
    conn.commit()
    return True


def atualizar_senha_usuario(email, nova_senha):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    usuario = cursor.fetchone()

    if usuario:
        senha_hash = generate_password_hash(nova_senha)
        cursor.execute(
            "UPDATE usuarios SET senha = %s WHERE email = %s", (senha_hash, email))
        conn.commit()
        return True
    return False