from gevent import monkey
monkey.patch_all()

import os
import webbrowser
from flask import Flask
from dotenv import load_dotenv
from app.routes.alunos_routes import alunos_bp
from app.routes.login_routes import login_routes
from app.routes.dashboard_routes import dashboard_routes
from app.routes.relatorios_routes import relatorios_bp
from app.routes.recognition_routes import recognition_bp
from app.services.relatorios_service import formatar_data
from app.extensions import socketio
from app.recognition.engine import carregar_face_model
import warnings
import logging
import signal
import sys

load_dotenv()

# Ignorar avisos de UserWarning e FutureWarning.
warnings.simplefilter("ignore", UserWarning)
warnings.simplefilter("ignore", FutureWarning)

# Configuração global de logging.
logging.basicConfig(level=logging.WARNING)  # Log de WARNING ou superior.
logger = logging.getLogger(__name__)  # Logger específico para este script.
logger.setLevel(logging.INFO)  # Permitir logs de INFO neste script (por exemplo, run.py).

# Logger específico para reconhecimento facial.
recognition_logger = logging.getLogger('recognition')
recognition_logger.setLevel(logging.INFO)

# Reduzir verbosidade de bibliotecas externas.
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('flask').setLevel(logging.ERROR)
logging.getLogger('onnxruntime').setLevel(logging.WARNING)
logging.getLogger('engineio').setLevel(logging.WARNING)

# Reduzir logs do gevent.
logging.getLogger('geventwebsocket.handler').setLevel(logging.ERROR)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

def create_app():
    app = Flask(__name__,
                template_folder='app/templates',
                static_folder='app/static')

    app.config.from_object(Config)
    app.jinja_env.filters['formatar_data'] = formatar_data

    app.register_blueprint(alunos_bp, url_prefix='/alunos')
    app.register_blueprint(login_routes)
    app.register_blueprint(dashboard_routes)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(recognition_bp)

    return app

def iniciar_socketio(app):
    socketio.init_app(app)

def carregar_modelos():
    logger.info("Iniciando carregamento do modelo de detecção facial...")
    try:
        carregar_face_model()
        logger.info("✅ Modelo carregado com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao carregar modelo: {e}")
        exit(1)


def signal_handler(sig, frame):
    print("\n🚪 Encerrando servidor com segurança...")
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    app = create_app()
    iniciar_socketio(app)
    carregar_modelos()

    # Aviso de inicialização do sistema.
    logger.info("Sistema iniciado com sucesso! Acesse em http://127.0.0.1:5000")
    logger.info("Para finalizar o servidor, pressione CTRL+C")

    # Abre o navegador automaticamente.
    webbrowser.open_new('http://127.0.0.1:5000/login')

    # Executa o servidor com o socketio.
    socketio.run(app, debug=False, use_reloader=False)