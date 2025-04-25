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
- **CRUD completo de alunos**: crie, visualize, edite e exclua alunos pela interface web.
- **Cadastro com envio de foto**, turma e turno, com validações e mensagens interativas.
- **Treinamento de rostos** armazenados com uso de embeddings otimizados.
- **Registro automático de entrada e saída** com data e hora no formato brasileiro (dd/mm/aaaa hh:mm:ss).
- **Controle de tempo entre registros** para o mesmo aluno, evitando múltiplas marcações em curto intervalo.
- **Interface web** com alertas persistentes por aluno, organizados por nome, e filtros de visualização por tipo de registro (entrada/saída).
- **Geração de relatórios** com filtros avançados (por aluno, turma, data e tipo de registro).
- **Exportação de relatórios** em formatos **PDF**, **Excel** e **TXT**.
- Banco de dados relacional **MySQL** para armazenar dados de alunos e registros de presença.
- **Comunicação em tempo real** via **WebSocket** (SocketIO), permitindo atualizações instantâneas na interface.
- **Otimizações de desempenho** para ambientes com muitos alunos (resize de imagem, controle de FPS).
- **InsightFace** para melhorar a precisão e a performance do reconhecimento facial.
- **Alertas mais detalhados**, como "Aluno reconhecido e entrada registrada" e "Aluno reconhecido e saída registrada".
- **Evita duplicação de alertas** por aluno, com controle de tempo configurável.
- **Mensagens de sucesso e erro** ao executar um registro, proporcionando uma experiência mais interativa.

---

## 🚀 Tecnologias Utilizadas

<div align="left" style="display: flex; flex-wrap: wrap; gap: 10px;">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" height="35" title="HTML5" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" height="35" title="CSS3" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" height="35" title="JavaScript" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="35" title="Python" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/opencv/opencv-original.svg" height="35" title="OpenCV" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mysql/mysql-original.svg" height="35" title="MySQL" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg" height="35" title="Pandas" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pytorch/pytorch-original.svg" height="35" title="PyTorch" />
</div>

---

### 🧠 Inteligência Artificial & Reconhecimento Facial
- [PyTorch](https://pytorch.org/) – framework de machine learning usado para redes neurais
- [TorchVision](https://pytorch.org/vision/) / [TorchAudio](https://pytorch.org/audio/) – suporte a visão computacional e áudio
- [InsightFace](https://github.com/deepinsight/insightface) – biblioteca para reconhecimento facial baseado em embeddings
- [ONNX Runtime](https://onnxruntime.ai/) – execução eficiente de modelos pré-treinados (CPU ou GPU)

### 🖼️ Processamento de Imagens
- [OpenCV](https://opencv.org/) – manipulação de imagens e captura de vídeo
- [Pillow](https://python-pillow.org/) – processamento e salvamento de imagens

### 📊 Manipulação de Dados e Relatórios
- [NumPy](https://numpy.org/) – arrays numéricos de alto desempenho
- [Pandas](https://pandas.pydata.org/) – manipulação e análise de dados
- [OpenPyXL](https://openpyxl.readthedocs.io/) – criação e leitura de arquivos Excel (.xlsx)
- [XlsxWriter](https://xlsxwriter.readthedocs.io/) – geração avançada de planilhas Excel
- [ReportLab](https://www.reportlab.com/) – geração de arquivos PDF

### 🌐 Backend e Comunicação em Tempo Real
- [Flask](https://flask.palletsprojects.com/) – microframework web para Python
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/) – comunicação WebSocket em tempo real
- [Flask-CORS](https://flask-cors.readthedocs.io/) – suporte a CORS
- [python-socketio](https://python-socketio.readthedocs.io/) – cliente e servidor WebSocket
- [python-engineio](https://python-engineio.readthedocs.io/) – motor de transporte para SocketIO
- [python-dotenv](https://pypi.org/project/python-dotenv/) – carregamento de variáveis de ambiente via `.env`

### 🐬 Banco de Dados MySQL
- [PyMySQL](https://pymysql.readthedocs.io/)
- [mysqlclient](https://github.com/PyMySQL/mysqlclient)
- [mysql-connector-python](https://dev.mysql.com/doc/connector-python/en/)

### 🎨 Frontend e Estilização
- [HTML5](https://developer.mozilla.org/pt-BR/docs/Web/HTML)
- [CSS3](https://developer.mozilla.org/pt-BR/docs/Web/CSS)
- [JavaScript](https://developer.mozilla.org/pt-BR/docs/Web/JavaScript)
- [Tailwind CSS](https://tailwindcss.com/) – framework CSS utilitário
- [FontAwesome](https://fontawesome.com/) – ícones para web

### 🛠️ Empacotamento e Build
- [auto-py-to-exe](https://github.com/brentvollebregt/auto-py-to-exe) – geração de executáveis com interface gráfica
- [setuptools](https://pypi.org/project/setuptools/) / [wheel](https://pypi.org/project/wheel/) – empacotamento de dependências

---

## 💻 Requisitos do Sistema

| **🔸 MÍNIMOS** | **🔹 RECOMENDADOS** |
|---------------|----------------------|
| Requer sistema e processador de 64 bits | Requer sistema e processador de 64 bits |
| **SO:** Windows 10 / Ubuntu 20.04 / macOS 10.15 | **SO:** Windows 10 ou 11 / Ubuntu 22.04 / macOS 12 |
| **Processador:** Intel Core i5-8250U / AMD Ryzen 5 2500U | **Processador:** Intel Core i5 de 9ª geração / AMD Ryzen 5 3600 |
| **Memória:** 8 GB de RAM | **Memória:** 16 GB de RAM |
| **Placa de vídeo:** Gráficos integrados Intel UHD 620 ou superior | **Placa de vídeo:** NVIDIA GTX 1050 ou superior (opcional, para CUDA) |
| **Armazenamento:** 256 GB SSD | **Armazenamento:** 512 GB SSD |
| **Webcam:** 720p (HD), 30 FPS, Foco fixo | **Webcam:** 1080p (Full HD), 30 FPS ou superior, Foco fixo |

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

- **Processamento Numérico e Dados**: `numpy`, `pandas`, `openpyxl`, `reportlab`, `XlsxWriter`
- **Visão Computacional**: `opencv-python`, `pillow`
- **Inteligência Artificial / Deep Learning**: `torch`, `torchvision`, `torchaudio`, `insightface`, `onnxruntime`
- **Backend Web**: `flask`, `flask-cors`, `flask-socketio`, `python-socketio`, `python-engineio`, `python-dotenv`
- **Banco de Dados MySQL**: `pymysql`, `mysqlclient`, `mysql-connector-python`

Caso queira instalar manualmente (não recomendado), aqui estão os comandos divididos por categoria:

```sh
pip install numpy==1.24.4 pandas==2.2.1 openpyxl==3.1.2 reportlab==4.1.0 XlsxWriter==3.1.2

pip install opencv-python==4.11.0.86 pillow==10.3.0

pip install torch==2.2.1 torchvision==0.17.1 torchaudio==2.2.1 insightface==0.7.3

# ⚙️ ONNX Runtime
# Use APENAS UMA das versões abaixo ⬇️
# 👉 Para computadores comuns (CPU)
pip install onnxruntime==1.21.0

# ⚡ Para quem tem placa de vídeo NVIDIA (GPU)
# Requer CUDA configurado corretamente
pip install onnxruntime-gpu==1.21.0

pip install flask==3.1.0 flask-cors==5.0.1 flask-socketio==5.3.0 python-dotenv==1.0.1 python-socketio==5.5.2 python-engineio==4.3.2

pip install pymysql==1.0.2
pip install mysqlclient==2.2.0
pip install mysql-connector-python==9.2.0

pip install "setuptools>=69.5.1" "wheel>=0.43.0"
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
CREATE DATABASE IF NOT EXISTS reconhecimento_facial
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE reconhecimento_facial;

-- Tabela de alunos
CREATE TABLE `alunos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(255) NOT NULL,
  `foto` varchar(255) NOT NULL,
  `turno` enum('manhã','tarde','integral') NOT NULL DEFAULT 'integral',
  `turma` varchar(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de configurações
CREATE TABLE `configuracoes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome_configuracao` varchar(255) NOT NULL,
  `valor` int(11) NOT NULL,
  `tipo` enum('minutos','horas') NOT NULL DEFAULT 'minutos',
  `descricao` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Inserindo configuração inicial
INSERT INTO `configuracoes` (`nome_configuracao`, `valor`, `tipo`, `descricao`) VALUES
('tempo_espera', 3, 'minutos', 'Tempo de espera entre registros de entrada e saída');

-- Tabela de fotos dos alunos
CREATE TABLE `fotos_alunos` (
  `id_foto` int(11) NOT NULL AUTO_INCREMENT,
  `id_aluno` int(11) NOT NULL,
  `foto_nome` varchar(255) NOT NULL,
  PRIMARY KEY (`id_foto`),
  KEY `id_aluno` (`id_aluno`),
  CONSTRAINT `fotos_alunos_ibfk_1` FOREIGN KEY (`id_aluno`) REFERENCES `alunos` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de registros de presença
CREATE TABLE `registros_presenca` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_aluno` int(11) DEFAULT NULL,
  `tipo_registro` enum('entrada','saida') NOT NULL,
  `data_hora` timestamp NOT NULL DEFAULT current_timestamp(),
  `turma` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_aluno` (`id_aluno`),
  CONSTRAINT `registros_presenca_ibfk_1` FOREIGN KEY (`id_aluno`) REFERENCES `alunos` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
│   ├── controle_tempo.py 
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
│   │   ├── 📂 imagens/ 
│   │   │     ├── favicon.png
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

- Suporta **nomes com espaços e acentos**, mantendo compatibilidade com a língua portuguesa.
- Utiliza **embeddings em cache** para acelerar o reconhecimento facial e reduzir o consumo de recursos.
- **Entradas e saídas automáticas** são determinadas com base no último registro do aluno.
- Evita **múltiplos alertas** em curto período para o mesmo aluno, garantindo precisão nos registros.
- **CRUD completo de alunos** disponível diretamente na interface web, com atualizações em tempo real.
- **Tempo mínimo entre registros** é configurável no banco de dados, oferecendo controle flexível sobre duplicações.

---

## 🛠️ Lógica do Projeto

### Módulo 1: Reconhecimento Facial e Cadastro

- **Cadastro de alunos** com nome, turma, turno e envio de foto pela interface web.
- **Fotos salvas** na pasta `fotos_alunos/` com o id, nome do aluno e turma.
- **Treinamento automático** após o cadastro: a imagem é convertida em um **embedding facial** com o InsightFace.
- **Embeddings armazenados em cache** na pasta `embeddings_cache/`, evitando reprocessamento e acelerando o reconhecimento facial.
- Durante o uso, o **rosto detectado** via webcam é comparado com os embeddings armazenados para identificar o aluno.
- **Registro automático de entrada ou saída** com base no último registro do aluno.
- **Sistema de alertas** por aluno, exibidos de forma clara e organizada na interface web.

### Módulo 2: Interface Web e Relatórios

- **Interface web interativa** para cadastro, visualização da câmera em tempo real e geração de relatórios.
- **Comunicação em tempo real** via **SocketIO** (WebSocket), permitindo atualizações instantâneas na interface.
- **Alertas visuais dinâmicos** informando ações realizadas (cadastro, reconhecimento, entrada/saída).
- **Relatórios filtráveis** por nome, turma, data e tipo de registro (entrada ou saída).
- **Exportação de relatórios** em formatos **PDF**, **Excel** e **TXT** com apenas um clique.
- **Interface moderna** utilizando **TailwindCSS** e componentes reutilizáveis para otimizar a experiência do usuário.

---

## 📬 Contato

Este projeto foi desenvolvido por **Angelita Luz**, com apoio fundamental de **Janes Cleston**, que idealizou o projeto e está presente em todas as fases — incentivando, ajudando a organizar, estruturar e melhorar cada detalhe. Agradeço imensamente pela confiança e pela oportunidade de construir isso juntos. 💙

👩‍💻 Angelita Luz  
🔗 [GitHub](https://github.com/angelluzk) • [LinkedIn](https://linkedin.com/in/angelitaluz)

👨‍💻 Janes Cleston  
🔗 [GitHub](https://github.com/jcleston) • [LinkedIn](https://www.linkedin.com/in/janescleston)

---