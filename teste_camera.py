import cv2
import time

CAMERA_INDEX = 0

print(f"Tentando abrir a câmera de índice {CAMERA_INDEX}...")
start_time = time.time()
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
init_duration = time.time() - start_time
print(f"cv2.VideoCapture levou: {init_duration:.4f}s")

if not cap.isOpened():
    print(f"Erro: Não foi possível abrir a câmera {CAMERA_INDEX}!")
else:
    print(f"Câmera {CAMERA_INDEX} aberta com sucesso.")
    ret, frame = cap.read()
    if ret:
        print("Primeiro frame lido com sucesso!")
    else:
        print("Erro ao ler o primeiro frame!")
    cap.release()
    print("Câmera liberada!")


# DIGITE python teste_camera.py na pasta raiz do projeto, PARA TESTAR O FUNCIONAMENTO DA WEBCAM!!! Dessa forma você garante que a webcam está funcionando no seu computador, caso não esteja funcionando ou esteja desconectada, vai aparecer o alerta de "Erro: Não foi possível abrir a câmera"; "Erro ao ler o primeiro frame!"