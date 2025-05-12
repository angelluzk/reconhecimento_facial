const socket = io.connect("http://127.0.0.1:5000");

const botaoWebcam = document.getElementById("botao-webcam");
const video = document.getElementById("video-stream");
const containerAlerts = document.getElementById("alerts-container");
const filtroElement = document.getElementById("filtro");
const modal = document.getElementById("modal-tempo");
const btnAbrir = document.getElementById("btn-abrir-tempo");
const btnCancelar = document.getElementById("btn-cancelar-tempo");
const form = document.getElementById("form-tempo");
const inputValor = document.getElementById("valor-tempo");
const selectTipo = document.getElementById("tipo-tempo");
const userIcon = document.getElementById("user-icon");
const userMenu = document.getElementById("user-menu");
const logoutButton = document.getElementById("btnLogout");

let webcamAtiva = false;
let bloqueado = false;

const toggleWebcam = async () => {
  if (bloqueado) return;
  bloqueado = true;

  botaoWebcam.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Carregando...';
  video.classList.remove("hidden");
  video.src = "/video_feed";

  try {
    const res = await fetch("/toggle_stream", { method: "POST" });
    const { ativo } = await res.json();

    webcamAtiva = ativo;
    botaoWebcam.innerHTML = webcamAtiva
      ? '<i class="fas fa-stop mr-2"></i> Desligar Webcam'
      : '<i class="fas fa-play mr-2"></i> Ligar Webcam';

    if (!webcamAtiva) {
      video.src = "";
      video.classList.add("hidden");
    }
  } catch (err) {
    console.error("Erro ao alternar webcam:", err);
    botaoWebcam.innerHTML = 'Erro! Tente novamente';
    video.src = "";
    video.classList.add("hidden");
    webcamAtiva = false;
  } finally {
    setTimeout(() => bloqueado = false, 1000);
  }
};

const desligarCameraNaSaida = () => {
  if (webcamAtiva) navigator.sendBeacon("/desligar_camera");
};

const renderizarAlerta = ({ nome, mensagem, tipo }) => {
  let alunoDiv = document.getElementById(`aluno-${nome}`);
  if (!alunoDiv) {
    alunoDiv = document.createElement("div");
    alunoDiv.className = "border-l-4 border-blue-500 pl-4";
    alunoDiv.id = `aluno-${nome}`;
    alunoDiv.innerHTML = `<div class="text-lg font-semibold text-gray-800 mb-2">${nome}</div>`;
    containerAlerts.prepend(alunoDiv);
  }

  const mensagens = alunoDiv.querySelectorAll(`.mensagem.${tipo}`);
  const icone = {
    entrada: '<i class="fas fa-sign-in-alt text-green-600"></i>',
    saida: '<i class="fas fa-sign-out-alt text-yellow-600"></i>',
    erro: '<i class="fas fa-times-circle text-red-600"></i>',
  }[tipo] || '';

  const html = `<span class="mr-2">${icone}</span> ${mensagem}`;

  if (mensagens.length === 0) {
    const nova = document.createElement("div");
    nova.className = `mensagem ${tipo} flex items-center bg-gray-100 p-3 rounded-md mb-2 text-base`;
    nova.dataset.tipo = tipo;
    nova.innerHTML = html;
    alunoDiv.appendChild(nova);
  } else {
    mensagens[0].innerHTML = html;
  }

  aplicarFiltro();
  rolarParaCimaSeNecessario();
};

const aplicarFiltro = () => {
  const filtro = filtroElement.value;
  document.querySelectorAll(".mensagem").forEach(msg => {
    msg.style.display = (filtro === "todos" || msg.dataset.tipo === filtro) ? "flex" : "none";
  });
};

const rolarParaCimaSeNecessario = () => {
  const { scrollTop, clientHeight, scrollHeight } = containerAlerts;
  if (scrollTop + clientHeight >= scrollHeight - 50) {
    containerAlerts.scrollTop = scrollHeight;
  }
};

const abrirModalTempo = async () => {
  try {
    const res = await fetch('/api/tempo-espera');
    const data = await res.json();
    inputValor.value = data.valor;
    selectTipo.value = data.tipo;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  } catch (err) {
    console.error('Erro ao buscar tempo:', err);
    alert('Erro ao carregar configuração de tempo.');
  }
};

const cancelarAlteracaoTempo = () => {
  modal.classList.add('hidden');
  modal.classList.remove('flex');
};

const salvarTempo = async (e) => {
  e.preventDefault();

  try {
    const res = await fetch('/api/tempo-espera', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        valor: parseInt(inputValor.value),
        tipo: selectTipo.value,
      })
    });

    if (res.ok) {
      alert('Tempo atualizado com sucesso!');
      cancelarAlteracaoTempo();
    } else {
      alert('Erro ao atualizar tempo.');
    }
  } catch (err) {
    console.error('Erro ao salvar tempo:', err);
    alert('Erro ao atualizar configuração.');
  }
};

userIcon.addEventListener('click', (e) => {
  e.stopPropagation();
  userMenu.classList.toggle('hidden');
});

document.addEventListener('click', (e) => {
  if (!userMenu.contains(e.target) && !userIcon.contains(e.target)) {
    userMenu.classList.add('hidden');
  }
});

botaoWebcam.addEventListener("click", toggleWebcam);
window.addEventListener("beforeunload", desligarCameraNaSaida);
btnAbrir.addEventListener('click', abrirModalTempo);
btnCancelar.addEventListener('click', cancelarAlteracaoTempo);
form.addEventListener('submit', salvarTempo);
logoutButton.addEventListener('click', () => window.location.href = '/logout');

socket.on('connect', () => console.log("✅ Conectado ao servidor SocketIO."));
socket.on('disconnect', () => console.log("❌ Desconectado do servidor SocketIO."));
socket.on('alerta', renderizarAlerta);

document.getElementById("anoAtual").textContent = new Date().getFullYear();