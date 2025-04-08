## 📸 Sistema de Reconhecimento Facial para Escolas

<p align="center">
  <img src="imagens/projeto_reconhecimento_facial.png" alt="Reconhecimento Facial" width="800"/>
  <br/>
  <em>📷 Interface Web do sistema de reconhecimento facial em funcionamento...</em>
</p>

Este projeto tem como objetivo registrar a entrada e saída de alunos automaticamente por meio de **reconhecimento facial**. Utilizando **Python**, **OpenCV** e **InsightFace**, o sistema identifica os rostos dos alunos e registra sua presença no banco de dados **MySQL**. A interface web baseada em **Flask** e **WebSockets** permite exibir vídeo em tempo real, alertas persistentes e relatórios completos.

---

## 🧠 Funcionalidades

- **Reconhecimento facial em tempo real** via webcam para identificar alunos automaticamente.
- **Cadastro de alunos** com nome, turma, turno e envio de foto.
- **Treinamento de rostos** armazenados com uso de embeddings otimizados.
- **Registro automático de entrada e saída** com data e hora no formato brasileiro (dd/mm/aaaa hh:mm:ss).
- **Interface web** com alertas persistentes por aluno, organizados por nome, e filtros de visualização por tipo de registro (entrada/saída).
- **Geração de relatórios** com filtros avançados (por aluno, turma, data e tipo de registro).
- **Exportação de relatórios** em formatos **PDF**, **Excel** e **TXT**.
- Banco de dados relacional **MySQL** para armazenar dados de alunos e registros de presença.
- **Comunicação em tempo real** via **WebSocket** (SocketIO), permitindo atualizações instantâneas na interface.
- **Otimizações de desempenho** para ambientes com muitos alunos (resize de imagem, controle de FPS).
- **InsightFace** para melhorar a precisão e a performance do reconhecimento facial.
- **Alertas mais detalhados**, como "Aluno reconhecido e entrada registrada" e "Aluno reconhecido e saída registrada".
- **Evita duplicação de alertas** por aluno, com controle de tempo para evitar múltiplos alertas em curto intervalo.
- **Mensagens de sucesso e erro** ao executar um registro, proporcionando uma experiência mais interativa.

---

## 🚀 Tecnologias Utilizadas

- **Python 3.7+**
- **InsightFace**
- **OpenCV**
- **Flask**
- **Flask-SocketIO**
- **Eventlet**
- **Flask-CORS**
- **python-dotenv**
- **MySQL**
- **PyMySQL / MySQLClient / mysql-connector-python**
- **Pillow**
- **Pandas**
- **OpenPyXL**
- **ReportLab**
- **Torch / TorchVision / TorchAudio**
- **Tailwind CSS**
- **FontAwesome**

---

## 📌 Requisitos de Instalação

Antes de iniciar o sistema, siga os passos abaixo para configurar o ambiente corretamente:

### 1️⃣ Instale o Python 3.7 ou superior
Baixe e instale o Python pelo site oficial: [https://www.python.org/downloads/](https://www.python.org/downloads/)

> **IMPORTANTE**: Durante a instalação, marque a opção **"Add Python to PATH"**.

### 2️⃣ Atualize o pip  
Abra um terminal e execute:  
```sh
python -m pip install --upgrade pip
```

### 3️⃣ Instale as dependências principais

Se você preferir, pode instalar todas as dependências de uma vez, executando o seguinte comando no terminal a partir da pasta do projeto:

```sh
pip install -r requisitos.txt
```

Caso prefira instalar manualmente, execute os seguintes comandos no terminal:

```sh
pip install numpy opencv-python
pip install flask flask-socketio
pip install pymysql mysqlclient mysql-connector-python
pip install python-dotenv flask-cors eventlet
pip install insightface onnxruntime pillow
pip install torch torchvision torchaudio
pip install pandas openpyxl reportlab
```

### 4️⃣ Configuração do Banco de Dados
Certifique-se de ter o **MySQL** instalado e crie o banco de dados com a seguinte estrutura:
```sql
CREATE DATABASE reconhecimento_facial;

USE reconhecimento_facial;

CREATE TABLE alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    foto VARCHAR(255) NOT NULL,
    turno ENUM('manhã','tarde','integral') NOT NULL DEFAULT 'integral',
    turma VARCHAR(10) NOT NULL
);

CREATE TABLE registros_presenca (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_aluno INT,
    tipo_registro ENUM('entrada', 'saida'),
    data_hora TIMESTAMP NOT NULL DEFAULT current_timestamp(),
    turma VARCHAR(10) NOT NULL,
    FOREIGN KEY (id_aluno) REFERENCES alunos(id)
);
```

### 5️⃣ Configuração das Variáveis de Ambiente
Crie um arquivo **.env** na raiz do projeto e adicione suas credenciais do banco de dados:
```ini
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=reconhecimento_facial
```

---

## 🎯 Estrutura do Projeto

```
📂 reconhecimento-facial  
├── 📂 database  
│   ├── __init__.py          
│   ├── connection.py        
│   └── reconhecimento_facil.sql    
├── 📂 modulo1_reconhecimento  
│   ├── __init__.py 
│   ├── cadastro.py         
│   ├── engine.py            
│   ├── stream.py            
│   ├── relatorios.py        
│   ├── 📂 fotos_alunos/        
│   └── 📂 embeddings_cache/    
├── 📂 web 
│   ├── 📂 static/ 
│   │   ├── 📂 css/ 
│   │   │     ├── cadastro.css
│   │   │     ├── index.css
│   │   ├── 📂 js/ 
│   │   │     ├── cadastro.js
│   │   │     ├── index.js
│   │   │     ├── relatorio.js
│   ├── 📂 templates/
│   │   ├── cadastro.html
│   │   ├── index.html       
│   │   └── relatorio.html   
│   ├── app.py               
├── .env                     
├── README.md                
└── requisitos.txt             
```

---

## ▶️ Como Executar o Projeto

### 1️⃣ Inicie o servidor Flask
Abra um terminal na pasta do projeto e execute:
```sh
python web/app.py
```

### 2️⃣ Acesse a Interface Web
Após iniciar o servidor, acesse no navegador:
```
http://127.0.0.1:5000
```
A câmera será ativada automaticamente e exibirá o vídeo em tempo real.

### 3️⃣ Reconhecimento Facial e Registro
- Quando um **rosto for reconhecido**, ele será identificado e um alerta será exibido na interface.
- O registro de **entrada ou saída** será salvo automaticamente no banco de dados.

---

## 📌 Observações

- As imagens dos alunos devem estar na pasta `fotos_alunos/`
- O nome da imagem deve ser igual ao nome do aluno cadastrado.
- Suporta nomes com espaços e acentos.
- Utiliza embeddings em cache para acelerar o reconhecimento.
- Entradas e saídas são diferenciadas com base no último registro.
- Evita múltiplos alertas em curto período para o mesmo aluno.

---

## 🛠️ Lógica do Projeto

### Módulo 1: Reconhecimento Facial e Cadastro

- Cadastro de alunos com nome, turma, turno e envio de foto pela interface web.
- Fotos salvas na pasta `fotos_alunos/` com o nome do aluno.
- Treinamento automático após o cadastro: a imagem é convertida em um **embedding facial** com o InsightFace.
- Embeddings são salvos em cache na pasta `embeddings_cache/`, evitando reprocessamento e acelerando o reconhecimento.
- Durante o uso, o rosto detectado via webcam é comparado com os embeddings armazenados.
- Registro automático de **entrada** ou **saída** com base no último registro do aluno.
- Sistema de alertas por aluno, exibidos de forma clara e organizada na interface.

### Módulo 2: Interface Web e Relatórios

- Interface web interativa para cadastro, visualização da câmera e relatórios.
- Comunicação em tempo real com **SocketIO** (WebSocket).
- Alertas visuais dinâmicos informando ações realizadas (cadastro, reconhecimento, entrada/saída).
- Relatórios filtráveis por nome, turma, data e tipo de registro (entrada ou saída).
- Exportação de relatórios em **PDF**, **Excel** e **TXT** com um clique.
- Interface moderna utilizando **TailwindCSS** e componentes reutilizáveis.

---