// Conecta ao servidor usando Socket.IO, permitindo comunicação em tempo real.
const socket = io.connect("http://127.0.0.1:5000");

// Captura os elementos da página para interagir com eles no código.
const botaoWebcam = document.getElementById("botao-webcam");
const video = document.getElementById("video-stream");
const modal = document.getElementById('modal-tempo');
const btnAbrir = document.getElementById('abrir-modal-tempo');
const btnCancelar = document.getElementById('btn-cancelar-tempo');
const form = document.getElementById('form-tempo');
const inputValor = document.getElementById('valor-tempo');
const selectTipo = document.getElementById('tipo-tempo');

// Variáveis para controle da webcam e bloqueio de ações rápidas.
let webcamAtiva = false;
let bloqueado = false;
let cameraIndex = 0;

// Evento de clique no botão da webcam.
botaoWebcam.addEventListener("click", async () => {
  if (bloqueado) return; // Se a ação estiver bloqueada, não faz nada.
  bloqueado = true; // Bloqueia o botão para evitar múltiplos cliques.

  try {
    // Envia uma solicitação ao servidor para alternar o estado da webcam.
    const resposta = await fetch("/toggle_stream", { method: "POST" });
    const dados = await resposta.json();

    webcamAtiva = dados.ativo; // Atualiza a variável webcamAtiva com o estado retornado.

    // Se a webcam foi ativada, mostra o vídeo e altera o texto do botão.
    if (webcamAtiva) {
      video.src = "/video_feed"; // Define a URL do feed de vídeo.
      video.classList.remove("hidden"); // Torna o vídeo visível.
      botaoWebcam.innerHTML = '<i class="fas fa-stop mr-2"></i> Desligar Webcam'; // Muda o texto do botão.
    } else {
      // Caso a webcam seja desativada, esconde o vídeo e altera o botão novamente.
      video.src = "";
      video.classList.add("hidden");
      botaoWebcam.innerHTML = '<i class="fas fa-play mr-2"></i> Ligar Webcam';
    }
  } catch (error) {
    console.error("Erro ao alternar webcam:", error);
  } finally {
    setTimeout(() => { bloqueado = false }, 1000);
  }
});

// Este evento ocorre antes de a página ser descarregada (fechada).
window.addEventListener("beforeunload", () => {
  if (webcamAtiva) {
    // Envia uma mensagem para o servidor desligar a webcam antes de sair.
    navigator.sendBeacon("/toggle_stream");
  }
});

// Eventos do Socket.IO para comunicar com o servidor.
socket.on('connect', () => console.log("✅ Conectado ao servidor SocketIO."));
socket.on('disconnect', () => console.log("❌ Desconectado do servidor SocketIO."));

// Quando o servidor envia um alerta, ele chama essa função para exibir o alerta na página.
socket.on('alerta', (data) => {
  console.log("🔔 Alerta recebido:", data.mensagem);
  renderizarAlerta(data);
});

// Função para renderizar o alerta na tela.
function renderizarAlerta({ nome, mensagem, tipo }) {
  const container = document.getElementById("alerts-container");

  const estaNoFinal = container.scrollTop + container.clientHeight >= container.scrollHeight - 50;

  let alunoDiv = document.getElementById(`aluno-${nome}`);
  if (!alunoDiv) {
    // Se o aluno não estiver na lista, cria uma nova div para ele.
    alunoDiv = document.createElement("div");
    alunoDiv.className = "border-l-4 border-blue-500 pl-4";
    alunoDiv.id = `aluno-${nome}`;
    alunoDiv.innerHTML = `<div class="text-lg font-semibold text-gray-800 mb-2">${nome}</div>`;
    container.prepend(alunoDiv); // Adiciona o aluno ao início da lista.
  }

  const mensagensExistentes = alunoDiv.querySelectorAll(`.mensagem.${tipo}`); // Verifica se já existe um alerta do tipo.
  const icone = tipo === "entrada"
    ? '<i class="fas fa-sign-in-alt text-green-600"></i>'
    : tipo === "saida"
      ? '<i class="fas fa-sign-out-alt text-yellow-600"></i>'
      : '<i class="fas fa-times-circle text-red-600"></i>';

  const novaMensagemHTML = `<span class="mr-2">${icone}</span> ${mensagem}`;

  // Se não houver nenhuma mensagem desse tipo, cria uma nova.
  if (mensagensExistentes.length === 0) {
    const nova = document.createElement("div");
    nova.className = `mensagem ${tipo} flex items-center bg-gray-100 p-3 rounded-md mb-2 text-base`;
    nova.setAttribute("data-tipo", tipo);
    nova.innerHTML = novaMensagemHTML;
    alunoDiv.appendChild(nova);
  } else {
    // Se já existe uma mensagem, apenas a atualiza.
    mensagensExistentes[0].innerHTML = novaMensagemHTML;
  }

  aplicarFiltro();

  if (estaNoFinal) {
    container.scrollTop = container.scrollHeight;
  }
}

// Função para aplicar o filtro de mensagens.
function aplicarFiltro() {
  const filtro = document.getElementById("filtro").value;
  const mensagens = document.querySelectorAll(".mensagem");

  mensagens.forEach(m => {
    const tipo = m.getAttribute("data-tipo");
    m.style.display = (filtro === "todos" || tipo === filtro) ? "flex" : "none";
  });
}

// Atualiza o ano na tela com o ano atual.
document.getElementById("anoAtual").textContent = new Date().getFullYear();

// Ao clicar no botão "Abrir Modal", carrega os dados do tempo de espera.
btnAbrir.addEventListener('click', async () => {
  try {
    const response = await fetch('/api/tempo-espera');
    const data = await response.json();
    inputValor.value = data.valor;
    selectTipo.value = data.tipo;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  } catch (error) {
    console.error('Erro ao buscar tempo:', error);
    alert('Erro ao carregar configuração de tempo.');
  }
});

// Ao clicar em "Cancelar", fecha o modal.
btnCancelar.addEventListener('click', () => {
  modal.classList.add('hidden');
  modal.classList.remove('flex');
});

// Ao submeter o formulário, envia os dados de configuração para o servidor.
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const valor = parseInt(inputValor.value);
  const tipo = selectTipo.value;

  try {
    const response = await fetch('/api/tempo-espera', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ valor, tipo })
    });

    if (response.ok) {
      alert('Tempo atualizado com sucesso!');
      modal.classList.add('hidden');
      modal.classList.remove('flex');
    } else {
      alert('Erro ao atualizar tempo.');
    }
  } catch (error) {
    console.error('Erro ao salvar tempo:', error);
    alert('Erro ao atualizar configuração.');
  }
});