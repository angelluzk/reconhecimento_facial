<h1 align="center">
  🎓📸 Sistema de Reconhecimento Facial para Escolas
</h1>

<p align="center">
  <img src="imagens/projeto_reconhecimento_facial.png" alt="Reconhecimento Facial" width="800"/>
  <br/>
  📷<em>Interface Web do sistema de reconhecimento facial em funcionamento...</em>
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

<div style="display: flex" align="left">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" height="35" title="HTML5" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" height="35" title="CSS3" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" height="35" title="JavaScript" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="35" title="Python" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/opencv/opencv-original.svg" height="35" title="OpenCV" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg" height="35" title="Flask" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/socketio/socketio-original.svg" height="35" title="Socket.IO" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mysql/mysql-original.svg" height="35" title="MySQL" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg" height="35" title="Pandas" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pytorch/pytorch-original.svg" height="35" title="PyTorch" />
</div>

<br/>

> 🔧 Outras ferramentas, bibliotecas e dependências:
> - **InsightFace**  
> - **Eventlet**  
> - **Flask-CORS**  
> - **python-dotenv**  
> - **PyMySQL / mysql-connector-python / MySQLClient**  
> - **Pillow**  
> - **OpenPyXL**  
> - **ReportLab**  
> - **TorchVision / TorchAudio**  
> - **FontAwesome**  
> - **Tailwind CSS**

---

## 💻 REQUISITOS DE SISTEMA

| **🔸 MÍNIMOS** | **🔹 RECOMENDADOS** |
|---------------|----------------------|
| Requer sistema e processador de 64 bits | Requer sistema e processador de 64 bits |
| **SO:** Windows 10 / Ubuntu 20.04 / macOS 10.15 | **SO:** Windows 10 ou 11 / Ubuntu 22.04 / macOS 12 |
| **Processador:** Intel Core i5-8250U / AMD Ryzen 5 2500U | **Processador:** Intel Core i5 de 9ª geração / AMD Ryzen 5 3600 |
| **Memória:** 8 GB de RAM | **Memória:** 16 GB de RAM |
| **Placa de vídeo:** Gráficos integrados Intel UHD 620 ou superior | **Placa de vídeo:** NVIDIA GTX 1050 ou superior (opcional, para CUDA) |
| **Armazenamento:** 256 GB SSD | **Armazenamento:** 512 GB SSD |
| **Webcam:** 720p (HD), 30 FPS | **Webcam:** 1080p (Full HD), 30 FPS ou superior |

## 📌 Requisitos de Instalação

Antes de iniciar o sistema, siga os passos abaixo para configurar o ambiente corretamente:

### 1️⃣ Instale o Python 3.10 (recomendado)

Baixe e instale o Python pelo site oficial:  
🔗 [https://www.python.org/downloads/release/python-3100/](https://www.python.org/downloads/release/python-3100/)

Link direto para baixar: 
🔗 [https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe](https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe)

> ⚠️ **IMPORTANTE**:  
> Durante a instalação, marque a opção **"Add Python to PATH"** antes de prosseguir.

#### 💡 Por que a versão 3.10?

Algumas bibliotecas usadas neste projeto (como `insightface`, `onnxruntime` e versões específicas do `torch`) **ainda não são totalmente compatíveis com o Python 3.11 ou superior**. Para evitar erros de instalação ou incompatibilidade durante o uso, recomendo fortemente utilizar o **Python 3.10**.

Se você já tiver uma versão diferente do Python instalada, recomendo o uso de um ambiente virtual com a versão correta. 

---

### 2️⃣ Instale o Visual Studio Build Tools

 - **Visual Studio Build Tools**: Baixe e instale [aqui](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Selecione a opção **"Desenvolvimento para C++ Desktop"**
   - Deixe marcada a versão do **MSVC v14.x (MSVC v142 ou mais recente)**.

**Finalize a instalação e reinicie o computador.**

---

### 3️⃣ Atualize o `pip`, `setuptools` e `wheel`

Antes de instalar as dependências, é importante garantir que você está com as ferramentas de build atualizadas:

```sh
python -m pip install --upgrade pip setuptools wheel
```

### 4️⃣ Instale todas as dependências do projeto

Você pode instalar tudo de uma vez com:

```sh
pip install -r requisitos.txt
```

Esse comando irá instalar todas as bibliotecas necessárias, incluindo:

- **Processamento Numérico e Dados**: `numpy`, `pandas`, `openpyxl`, `reportlab`
- **Visão Computacional**: `opencv-python`, `pillow`
- **Inteligência Artificial / Deep Learning**: `torch`, `torchvision`, `torchaudio`, `insightface`, `onnxruntime`
- **Backend Web**: `flask`, `flask-cors`, `flask-socketio`, `eventlet`, `python-dotenv`
- **Banco de Dados MySQL**: `pymysql`, `mysqlclient`, `mysql-connector-python`

Caso queira instalar manualmente (não recomendado), aqui estão os comandos divididos por categoria:

```sh
pip install numpy==1.24.4 pandas==2.2.1 openpyxl==3.1.2 reportlab==4.1.0

pip install opencv-python==4.11.0.86 pillow==10.3.0

pip install torch==2.2.1 torchvision==0.17.1 torchaudio==2.2.1 insightface==0.7.3

# ⚙️ ONNX Runtime
# Use APENAS UMA das versões abaixo ⬇️
# 👉 Para computadores comuns (CPU)
pip install onnxruntime==1.21.0

# ⚡ Para quem tem placa de vídeo NVIDIA (GPU)
# Requer CUDA configurado corretamente
pip install onnxruntime-gpu==1.21.0

pip install flask==3.1.0 flask-cors==5.0.1 flask-socketio==5.3.0 eventlet==0.33.0 python-dotenv==1.0.1

pip install pymysql==1.0.2 mysqlclient==2.2.0 mysql-connector-python==9.2.0

pip install setuptools>=69.5.1 wheel>=0.43.0
```

---

### 5️⃣ Instale e configure o MySQL

Para que o sistema funcione corretamente, é necessário ter o **MySQL** instalado localmente.

#### ✅ Recomendado: MySQL 8.0.33 ou superior (Community Edition)

- Baixe pelo site oficial: [https://dev.mysql.com/downloads/mysql/](https://dev.mysql.com/downloads/mysql/)
- Durante a instalação, **selecione o método de autenticação _Legacy_ (`mysql_native_password`)**, caso a opção seja oferecida.

> ⚠️ Evite usar versões muito antigas (como a 5.x), pois podem causar **incompatibilidades com os conectores utilizados no projeto** (`mysqlclient`, `pymysql`, `mysql-connector-python`).

---

#### 🗃️ Criação do banco de dados e tabelas

Com o MySQL instalado e em execução, abra o terminal do MySQL e execute os comandos abaixo para criar o banco de dados e suas respectivas tabelas:

```sql
CREATE DATABASE reconhecimento_facial;

USE reconhecimento_facial;

CREATE TABLE alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    foto VARCHAR(255) NOT NULL,
    turno ENUM('manhã', 'tarde', 'integral') NOT NULL DEFAULT 'integral',
    turma VARCHAR(10) NOT NULL
);

CREATE TABLE `fotos_alunos` (
  `id_foto` int(11) NOT NULL,
  `id_aluno` int(11) NOT NULL,
  `foto_nome` varchar(255) NOT NULL
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
---

### 6️⃣ Configuração das Variáveis de Ambiente
Crie um arquivo **.env** na raiz do projeto e adicione suas credenciais do banco de dados:
```ini
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=reconhecimento_facial
```
> Esse arquivo armazena as **credenciais de acesso ao banco de dados** de forma segura, evitando a exposição de dados sensíveis no código.

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
│   ├── crud_alunos.py        
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
│   │   │     ├── alunos.js
│   │   │     ├── cadastro.js
│   │   │     ├── index.js
│   │   │     ├── relatorio.js
│   ├── 📂 templates/
│   │   ├── alunos.html
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

## 📬 Contato

Este projeto foi desenvolvido por **Angelita Luz**, com apoio fundamental de **Janes Cleston**, que idealizou o projeto e está presente em todas as fases — incentivando, ajudando a organizar, estruturar e melhorar cada detalhe. Agradeço imensamente pela confiança e pela oportunidade de construir isso juntos. 💙

👩‍💻 Angelita Luz  
🔗 [GitHub](https://github.com/angelluzk) • [LinkedIn](https://linkedin.com/in/angelitaluz)

👨‍💻 Janes Cleston  
🔗 [GitHub](https://github.com/jcleston) • [LinkedIn](https://www.linkedin.com/in/janescleston)

---