## 📸 Sistema de Reconhecimento Facial para Escolas

Este projeto tem como objetivo registrar a entrada e saída de alunos automaticamente por meio de **reconhecimento facial**. Utilizando **Python**, **OpenCV** e **InsightFace**, o sistema identifica os rostos dos alunos e registra sua presença no banco de dados **MySQL**. A interface web baseada em **Flask** e **WebSockets** permite exibir vídeo em tempo real, alertas persistentes e relatórios completos.

---

## 📸 Funcionalidades

- **Reconhecimento facial em tempo real** via webcam para identificar alunos automaticamente.
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

- **Python 3.7+** – Linguagem principal utilizada no projeto.
- **InsightFace** – Biblioteca de reconhecimento facial baseada em deep learning.
- **OpenCV** – Processamento de vídeo e imagens, integração com webcam.
- **Flask** – Framework web leve para a criação da interface e API.
- **Flask-SocketIO** – Comunicação em tempo real entre servidor e cliente via WebSockets.
- **Eventlet** – Gerenciador de conexões assíncronas para suporte ao Flask-SocketIO.
- **Flask-CORS** – Permite comunicação segura entre o backend e frontend hospedados em origens diferentes.
- **python-dotenv** – Carrega automaticamente variáveis de ambiente a partir de um arquivo `.env`.
- **MySQL** – Banco de dados relacional utilizado para armazenar os registros e dados dos alunos.
- **PyMySQL / MySQLClient / mysql-connector-python** – Conectores Python para integração com o banco de dados MySQL.
- **Pillow** – Processamento de imagens para leitura e manipulação das fotos dos alunos.
- **Pandas** – Manipulação de dados tabulares, usado para relatórios.
- **OpenPyXL** – Exportação de planilhas Excel.
- **ReportLab** – Geração de arquivos PDF.
- **Tailwind CSS** – Framework CSS para construção da interface moderna e responsiva.
- **FontAwesome** – Ícones vetoriais para compor a interface visual.

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
    foto LONGBLOB NOT NULL,
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
│   ├── __init__.py          # Inicialização do módulo de banco de dados  
│   └── connection.py        # Conexão com o banco de dados  
├── 📂 modulo1_reconhecimento  
│   ├── __init__.py          # Inicialização do módulo de reconhecimento  
│   ├── engine.py            # Funções de reconhecimento facial com InsightFace  
│   ├── stream.py            # Lógica de captura de vídeo ao vivo e streaming  
│   ├── relatorios.py        # Geração de relatórios de presença  
│   └── fotos_alunos/        # Pasta com fotos dos alunos cadastrados  
├── 📂 web  
│   ├── app.py               # Servidor Flask + WebSocket  
│   ├── templates/  
│   │   ├── index.html       # Interface da webcam e alertas  
│   │   └── relatorio.html   # Relatório de presença  
├── .env                     # Variáveis de ambiente (configurações do banco de dados)  
├── README.md                # Documentação do projeto  
└── requisitos.txt           # Lista de dependências  
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

## 📌 Observações Importantes

- As imagens dos alunos devem ser salvas na pasta **modulo1_reconhecimento/fotos_alunos/**
- O nome dos arquivos deve corresponder ao nome do aluno cadastrado no banco de dados (exemplo: **João Alves de Souza.jpg** ou **joao_alves.jpg**). O sistema suporta nomes com espaços e acentos.
- O sistema diferencia **entrada** e **saída** verificando o último registro do aluno.
- **Evita duplicação de alertas** por aluno, com um controle para que o mesmo aluno não gere múltiplos alertas em um curto intervalo.

---

## 🛠️ Lógica do Projeto

### Módulo 1: Reconhecimento Facial

- **Função principal**: O sistema utiliza a biblioteca **InsightFace** para realizar o reconhecimento facial. O rosto do aluno é detectado pela webcam em tempo real e comparado com as fotos cadastradas na pasta `fotos_alunos`.
  
- **Registros de Entrada e Saída**: Quando o rosto de um aluno é reconhecido, o sistema registra automaticamente a entrada ou saída no banco de dados, com a data e hora no formato brasileiro (dd/mm/aaaa hh:mm:ss).

- **Alertas**: Os alertas são exibidos na interface, indicando o nome do aluno e o tipo de registro (entrada ou saída). A lista de alertas é persistente, organizada por aluno, e contém cabeçalhos identificando o nome do aluno. As mensagens de alerta são detalhadas e não desaparecem rapidamente para que os operadores possam acompanhar claramente cada aluno que passou pela câmera.

---

### Módulo 2: Interface Web e Relatórios

- **Interface com WebSocket**: A comunicação em tempo real é realizada via **Flask-SocketIO**, permitindo que os alertas e registros sejam atualizados na interface sem a necessidade de recarregar a página.

- **Relatórios**: A interface oferece a opção de gerar relatórios detalhados sobre os registros de presença. Os relatórios podem ser filtrados por aluno, data ou turma, e exportados para os formatos **PDF**, **Excel** ou **TXT**.

---