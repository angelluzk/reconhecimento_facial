import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STORAGE_DIR = os.path.join(BASE_DIR, 'storage')

FOTOS_ALUNOS_DIR = os.path.join(STORAGE_DIR, 'fotos_alunos')
EMBEDDINGS_DIR = os.path.join(STORAGE_DIR, 'embeddings_cache')

os.makedirs(FOTOS_ALUNOS_DIR, exist_ok=True)
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)