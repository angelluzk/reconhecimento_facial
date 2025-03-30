import face_recognition as fr

# Está função reconhe os rostos em uma imagem fornecida
def reconhece_face(url_foto):
    foto = fr.load_image_file(url_foto)
    rostos = fr.face_encodings(foto)

    if len(rostos) > 0:
        return True, rostos
    return False, []

# Está função é para obter a lista de rostos conhecidos e seus respectivos nomes
def get_rostos():
    rostos_conhecidos = []
    nomes_dos_rostos = []

    arquivos = [
        ("Aluno1", "./fotos_alunos/aluno1.jpg"),
        ("Aluno2", "./fotos_alunos/aluno2.jpg")
    ]

    for nome, caminho in arquivos:
        sucesso, rostos = reconhece_face(caminho)
        if sucesso:
            rostos_conhecidos.append(rostos[0])
            nomes_dos_rostos.append(nome)

    return rostos_conhecidos, nomes_dos_rostos