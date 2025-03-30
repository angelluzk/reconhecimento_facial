import numpy as np
import face_recognition as fr
import cv2
from engine import get_rostos

rostos_conhecidos, nomes_dos_rostos = get_rostos()

video_capture = cv2.VideoCapture(0) # Inicia a captura de vídeo da webcam (0 representa a primeira webcam disponível)

# Loop contínuo para capturar e processar os frames da webcam
while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Erro ao capturar o frame da câmera.")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Converte o frame BGR para RGB

    localizacao_dos_rostos = fr.face_locations(rgb_frame) # Detecta a localização dos rostos no frame

    if not localizacao_dos_rostos:
        print("Nenhum rosto detectado.")
        cv2.imshow('Webcam_facerecognition', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    rostos_desconhecidos = fr.face_encodings(rgb_frame, localizacao_dos_rostos) # Codifica os rostos detectados no frame

    if not rostos_desconhecidos:
        print("Nenhum rosto encontrado.")
        continue

    # Para cada rosto detectado, compara com os rostos conhecidos e exibe o nome se encontrado
    for (top, right, bottom, left), rosto_desconhecido in zip(localizacao_dos_rostos, rostos_desconhecidos):
        resultados = fr.compare_faces(rostos_conhecidos, rosto_desconhecido)
        face_distances = fr.face_distance(rostos_conhecidos, rosto_desconhecido)

        # Se houver uma correspondência, exibe o nome, caso contrário, exibe "Desconhecido"
        if len(face_distances) > 0:
            melhor_id = np.argmin(face_distances)
            nome = nomes_dos_rostos[melhor_id] if resultados[melhor_id] else "Desconhecido"
        else:
            nome = "Desconhecido"

        # Desenha um retângulo ao redor do rosto e coloca o nome do aluno
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        cv2.putText(frame, nome, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 1)

    cv2.imshow('Webcam_facerecognition', frame)

    # Encerra o loop se a tecla "q" for pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()