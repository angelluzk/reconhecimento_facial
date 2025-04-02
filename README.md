# 📸 Sistema de Reconhecimento Facial para Escolas

Este projeto tem como objetivo registrar a entrada e saída de alunos automaticamente por meio de **reconhecimento facial**. Utilizando **Python**, **OpenCV** e **face_recognition**, o sistema identifica os rostos dos alunos e registra sua presença no banco de dados **MySQL**. O sistema conta com uma interface web simples baseada em **Flask** e **WebSockets** para exibir o vídeo em tempo real e alertas sobre os reconhecimentos.

---

## 🚀 Tecnologias Utilizadas

- **Python 3.7+**
- **OpenCV** (Processamento de imagens)
- **Face Recognition** (Reconhecimento facial baseado em dlib)
- **Flask** (Framework para aplicação web)
- **Flask-SocketIO** (Comunicação em tempo real via WebSocket)
- **MySQL** (Banco de dados para armazenamento dos registros de presença)

---

## 📌 Requisitos de Instalação

Antes de iniciar o sistema, siga os passos abaixo para configurar o ambiente corretamente:

### 1️⃣ Instale o Python 3.7 ou superior
Baixe e instale o Python pelo site oficial: [https://www.python.org/downloads/](https://www.python.org/downloads/)

> **IMPORTANTE**: Durante a instalação, marque a opção **"Add Python to PATH"**.

### 2️⃣ Instale CMake e Visual Studio Build Tools
Esses pacotes são necessários para compilar o **dlib**, que é usado pelo **face_recognition**.

- **CMake**: Baixe e instale [aqui](https://cmake.org/download/) (Marque a opção **"Add CMake to system PATH"**)
- **Visual Studio Build Tools**: Baixe e instale [aqui](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
  - Selecione a opção **"Desenvolvimento para C++ Desktop"**

### 3️⃣ Atualize o pip
Abra um terminal e execute:
```sh
python -m pip install --upgrade pip
```

### 4️⃣ Instale as dependências principais
Execute os seguintes comandos no terminal:
```sh
pip install dlib
pip install face_recognition
pip install numpy opencv-python
pip install flask flask-socketio
pip install pymysql mysqlclient mysql-connector-python
pip install python-dotenv flask-cors eventlet
```

### 5️⃣ Configuração do Banco de Dados
Certifique-se de ter o **MySQL** instalado e crie o banco de dados com a seguinte estrutura:
```sql
CREATE DATABASE reconhecimento_facial;

USE reconhecimento_facial;

CREATE TABLE alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);

CREATE TABLE registros_presenca (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_aluno INT,
    tipo_registro ENUM('entrada', 'saida'),
    data_hora DATETIME,
    FOREIGN KEY (id_aluno) REFERENCES alunos(id)
);
```

### 6️⃣ Configuração das Variáveis de Ambiente
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
│   ├── connection.py   # Conexão com o banco de dados
├── 📂 modulo1_reconhecimento
│   ├── engine.py       # Funções de reconhecimento e registro
│   ├── fotos_alunos/   # Pasta com imagens dos alunos cadastrados
├── 📂 web
│   ├── templates/
│   │   ├── index.html  # Página principal com vídeo ao vivo
│   ├── app.py         # Servidor Flask para interface web
├── .env               # Configurações do banco de dados
├── README.md          # Documentação do projeto
└── requisitos.txt     # Lista de dependências
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
- O nome dos arquivos deve corresponder ao nome do aluno cadastrado no banco de dados (exemplo: **joao_silva.jpg**).
- O sistema diferencia **entrada** e **saída** verificando o último registro do aluno.

---

## 🛠️ Futuras Melhorias

- 📌 Interface de cadastro de alunos
- 📌 Melhor otimização do reconhecimento facial
- 📌 Relatórios de presença por período
- 📌 Integração com RFID para aumentar a precisão

---

## 🤝 Contribuição
Se quiser contribuir com melhorias, sinta-se à vontade para abrir um **Pull Request** ou relatar problemas na aba **Issues** do repositório!

---

## 📜 Licença
Este projeto é de código aberto e pode ser utilizado para fins educacionais e acadêmicos. 🚀

