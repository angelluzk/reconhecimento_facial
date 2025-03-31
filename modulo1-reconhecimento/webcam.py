# Módulo responsável por capturar a imagem da webcam e identificar os rostos.
import numpy as np
import face_recognition as fr
import cv2
from engine import get_rostos, registrar_ocorrencia

rostos_conhecidos, nomes_dos_rostos = get_rostos() # Carrega os rostos conhecidos e seus respectivos nomes.

video_capture = cv2.VideoCapture(0) # Inicia a captura de vídeo.

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Erro ao capturar o frame da câmera.")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    localizacao_dos_rostos = fr.face_locations(rgb_frame)
    rostos_desconhecidos = fr.face_encodings(rgb_frame, localizacao_dos_rostos)

    for (top, right, bottom, left), rosto_desconhecido in zip(localizacao_dos_rostos, rostos_desconhecidos):
        face_distances = fr.face_distance(rostos_conhecidos, rosto_desconhecido)
        melhor_id = np.argmin(face_distances) if len(face_distances) > 0 else -1
        nome = nomes_dos_rostos[melhor_id] if melhor_id != -1 and fr.compare_faces(rostos_conhecidos, rosto_desconhecido)[melhor_id] else "Desconhecido"
        
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, nome, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 1)

        if nome != "Desconhecido":
            registrar_ocorrencia(nome)
            print(f"Rosto de {nome} reconhecido e registrado.")

    cv2.imshow('Webcam', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
