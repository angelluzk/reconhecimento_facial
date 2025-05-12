from flask import Blueprint, render_template
from app.services.dashboard_service import get_dashboard_data
import json
from flask import send_from_directory
from app.utils.caminhos import FOTOS_ALUNOS_DIR

dashboard_routes = Blueprint('dashboard_routes', __name__)

@dashboard_routes.route('/storage/fotos_alunos/<filename>')
def serve_foto(filename):
    return send_from_directory(FOTOS_ALUNOS_DIR, filename)

@dashboard_routes.route('/dashboard')
def dashboard():
    dados_dashboard = get_dashboard_data()

    dados_dashboard['semana_labels'] = json.dumps(dados_dashboard['semana_labels'])
    dados_dashboard['semana_presencas'] = json.dumps(dados_dashboard['semana_presencas'])
    dados_dashboard['turno_counts'] = json.dumps(dados_dashboard['turno_counts'])

    return render_template('dashboard.html', **dados_dashboard)