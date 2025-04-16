const socket = io.connect("http://127.0.0.1:5000");
const botaoWebcam = document.getElementById("botao-webcam");
const video = document.getElementById("video-stream");
const botaoTrocarCamera = document.getElementById("trocar-camera");
const modal = document.getElementById('modal-tempo');
const btnAbrir = document.getElementById('abrir-modal-tempo');
const btnCancelar = document.getElementById('btn-cancelar-tempo');
const form = document.getElementById('form-tempo');
const inputValor = document.getElementById('valor-tempo');
const selectTipo = document.getElementById('tipo-tempo');
let webcamAtiva = false;
let bloqueado = false;
let cameraIndex = 0;

botaoWebcam.addEventListener("click", async () => {
  if (bloqueado) return;
  bloqueado = true;

  try {
    const resposta = await fetch("/toggle_stream", { method: "POST" });
    const dados = await resposta.json();

    webcamAtiva = dados.ativo;
    if (webcamAtiva) {
      video.src = "/video_feed";
      video.classList.remove("hidden");
      botaoWebcam.innerHTML = '<i class="fas fa-stop mr-2"></i> Desligar Webcam';
    } else {
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

botaoTrocarCamera.addEventListener("click", () => {
  cameraIndex = cameraIndex === 0 ? 1 : 0;
  socket.emit("trocar_camera", { index: cameraIndex });
});

window.addEventListener("beforeunload", () => {
  if (webcamAtiva) {
    navigator.sendBeacon("/toggle_stream");
  }
});

socket.on('connect', () => console.log("✅ Conectado ao servidor SocketIO."));
socket.on('disconnect', () => console.log("❌ Desconectado do servidor SocketIO."));

socket.on('alerta', (data) => {
  console.log("🔔 Alerta recebido:", data.mensagem);
  renderizarAlerta(data);
});

function renderizarAlerta({ nome, mensagem, tipo }) {
    const container = document.getElementById("alerts-container");

    const estaNoFinal = container.scrollTop + container.clientHeight >= container.scrollHeight - 50;
  
    let alunoDiv = document.getElementById(`aluno-${nome}`);
    if (!alunoDiv) {
      alunoDiv = document.createElement("div");
      alunoDiv.className = "border-l-4 border-blue-500 pl-4";
      alunoDiv.id = `aluno-${nome}`;
      alunoDiv.innerHTML = `<div class="text-lg font-semibold text-gray-800 mb-2">${nome}</div>`;
      container.prepend(alunoDiv);
    }
  
    const mensagensExistentes = alunoDiv.querySelectorAll(`.mensagem.${tipo}`);
    const icone = tipo === "entrada"
      ? '<i class="fas fa-sign-in-alt text-green-600"></i>'
      : tipo === "saida"
        ? '<i class="fas fa-sign-out-alt text-yellow-600"></i>'
        : '<i class="fas fa-times-circle text-red-600"></i>';
  
    const novaMensagemHTML = `<span class="mr-2">${icone}</span> ${mensagem}`;
  
    if (mensagensExistentes.length === 0) {
      const nova = document.createElement("div");
      nova.className = `mensagem ${tipo} flex items-center bg-gray-100 p-3 rounded-md mb-2 text-base`;
      nova.setAttribute("data-tipo", tipo);
      nova.innerHTML = novaMensagemHTML;
      alunoDiv.appendChild(nova);
    } else {
      mensagensExistentes[0].innerHTML = novaMensagemHTML;
    }
  
    aplicarFiltro();
  
    if (estaNoFinal) {
      container.scrollTop = container.scrollHeight;
    }
  }
  
function aplicarFiltro() {
  const filtro = document.getElementById("filtro").value;
  const mensagens = document.querySelectorAll(".mensagem");

  mensagens.forEach(m => {
    const tipo = m.getAttribute("data-tipo");
    m.style.display = (filtro === "todos" || tipo === filtro) ? "flex" : "none";
  });
}

document.getElementById("anoAtual").textContent = new Date().getFullYear();

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

btnCancelar.addEventListener('click', () => {
  modal.classList.add('hidden');
  modal.classList.remove('flex');
});

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