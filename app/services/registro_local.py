import json
from datetime import datetime

ARQUIVO_REGISTRO = "registros_presenca.json"

def registrar_evento(nome, evento):
    try:
        with open(ARQUIVO_REGISTRO, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        dados = []

    dados.append({
        "aluno": nome,
        "evento": evento,
        "data": datetime.now().strftime("%Y-%m-%d"),
        "hora": datetime.now().strftime("%H:%M:%S")
    })

    with open(ARQUIVO_REGISTRO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)