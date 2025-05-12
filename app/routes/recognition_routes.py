from flask import Blueprint, jsonify, request, Response, render_template
from app.recognition.stream import (
    liberar_camera, iniciar_camera, recarregar_embeddings, streaming, gerar_frames
)
from app.services.controle_temp_service import (
    obter_configuracao_tempo, atualizar_configuracao_tempo
)
from app.extensions import socketio
import logging

recognition_bp = Blueprint('face_recognition', __name__)

logger = logging.getLogger(__name__)

def alternar_webcam():
    global streaming
    if not streaming:
        iniciar_camera()
        streaming = True
        logger.info("🎥 Webcam ligada!")
    else:
        liberar_camera()
        streaming = False
        logger.info("🎥 Webcam desligada!")

@recognition_bp.route('/')
def recognition():
    return render_template('recognition.html')

@recognition_bp.route('/video_feed')
def video_feed():
    if not streaming:
        return '', 204
    return Response(gerar_frames(socketio),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@recognition_bp.route('/toggle_stream', methods=['POST'])
def toggle_stream():
    try:
        alternar_webcam()
        return jsonify({'ativo': streaming})
    except Exception as e:
        logger.error(f"❌ Erro ao alternar webcam: {e}")
        return jsonify({'erro': 'Erro ao alternar webcam'}), 500

@recognition_bp.route('/desligar_camera', methods=['POST'])
def desligar_camera():
    try:
        if streaming:
            liberar_camera()
            logger.info("🔌 Webcam desligada por mudança de página!")
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"❌ Erro ao desligar webcam: {e}")
        return jsonify({'erro': 'Erro ao desligar webcam'}), 500

@recognition_bp.route('/api/tempo-espera', methods=['GET'])
def get_tempo_espera():
    try:
        config = obter_configuracao_tempo()
        if config:
            return jsonify({"valor": int(config["valor"]), "tipo": config["tipo"]})
        return jsonify({"error": "Configuração não encontrada"}), 404
    except Exception as e:
        logger.error(f"❌ Erro ao obter tempo de espera: {e}")
        return jsonify({"erro": "Erro ao obter tempo de espera"}), 500

@recognition_bp.route('/api/tempo-espera', methods=['POST'])
def set_tempo_espera():
    data = request.get_json()
    valor = data.get("valor")
    tipo = data.get("tipo")
    if valor and tipo in ["minutos", "horas"]:
        try:
            atualizar_configuracao_tempo(valor, tipo)
            return jsonify({"message": "Configuração atualizada com sucesso"})
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar configuração de tempo: {e}")
            return jsonify({"erro": "Erro ao atualizar configuração de tempo"}), 500
    return jsonify({"error": "Dados inválidos"}), 400

@recognition_bp.route('/recarregar_embeddings', methods=['POST'])
def atualizar_embeddings():
    try:
        if streaming:
            liberar_camera()
            iniciar_camera()
        total = recarregar_embeddings()
        return jsonify({"mensagem": f"{total} embeddings recarregados com sucesso. A câmera foi reiniciada."})
    except Exception as e:
        logger.error(f"❌ Erro ao recarregar embeddings: {e}")
        return jsonify({"erro": "Erro ao recarregar embeddings."}), 500