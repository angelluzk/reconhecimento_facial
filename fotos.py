import face_recognition as fr
from engine import reconhece_face, get_rostos

desconhecido = reconhece_face("./fotos_alunos/desconhecido.jpg") # Carrega a imagem do rosto desconhecido e tenta reconhecer um rosto nela

# Aqui verifica se algum rosto foi encontrado na imagem
if desconhecido[0]:
    rosto_desconhecido = desconhecido[1][0]
    rostos_conhecidos, nomes_dos_rostos = get_rostos()
    resultados = fr.compare_faces(rostos_conhecidos, rosto_desconhecido)
    print(resultados)

    # Para cada comparação, verifica se o rosto foi reconhecido e exibe o nome correspondente
    for i, resultado in enumerate(resultados):
        if resultado:
            print(f"Rosto do {nomes_dos_rostos[i]} foi reconhecido")
else:
    print("Nenhum rosto encontrado na imagem.")
