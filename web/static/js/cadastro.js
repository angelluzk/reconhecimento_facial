// Referências aos elementos da interface.
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const form = document.getElementById('cadastro-form');
const statusText = document.getElementById('status');
const previewContainer = document.getElementById('preview-container');
const modal = document.getElementById('successModal');
const modalContent = document.getElementById('modalContent');
const repetirBtn = document.getElementById('repetirCadastro');
const successSound = document.getElementById('successSound');
const botaoWebcam = document.getElementById('botao-webcam');
const botaoCaptura = document.getElementById('botao-captura');
const fecharModalBtn = document.getElementById('fecharModal');
const loader = document.getElementById('loader');

// Variáveis de controle.
let stream = null;
let webcamLigada = false;
let bloqueado = false;
let cameraFrontal = true;

// Função para ligar a webcam.
async function ligarWebcam() {
  if (stream) desligarWebcam(); // Desliga se já estiver ligada.
  try {
    // Solicita permissão e ativa a câmera (frontal ou traseira).
    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: cameraFrontal ? "user" : "environment"
      }
    });
    video.srcObject = stream;
    video.classList.remove("hidden"); 
    document.getElementById('filtro')?.classList.remove("hidden"); // 👈 mostra filtro.
    botaoWebcam.innerHTML = '<i class="fas fa-stop mr-1"></i> Desligar Webcam';
    webcamLigada = true;
  } catch (error) {
    statusText.textContent = "Erro ao acessar a câmera: " + error.message;
  }
}

// Função para desligar a webcam.
function desligarWebcam() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop()); // Para todas as tracks de vídeo.
    stream = null;
  }
  video.classList.add("hidden");
  video.srcObject = null;
  document.getElementById('filtro')?.classList.add("hidden"); // 👈 esconde filtro.
  webcamLigada = false;
  botaoWebcam.innerHTML = '<i class="fas fa-play mr-1"></i> Ligar Webcam';
}

// Alterna webcam ligada/desligada ao clicar no botão.
botaoWebcam.addEventListener("click", () => {
  webcamLigada ? desligarWebcam() : ligarWebcam();
});

// Captura das imagens ao clicar no botão de captura.
botaoCaptura.addEventListener('click', async e => {
  e.preventDefault();
  if (bloqueado) return;
  bloqueado = true;

   // Impede captura se a webcam não estiver ligada.
  if (!webcamLigada) {
    alert("Ligue a webcam antes de iniciar a captura!");
    bloqueado = false;
    return;
  }

  previewContainer.innerHTML = ""; // Limpa pré-visualizações anteriores.

  const formData = new FormData(form);

  // Normaliza nome: caixa alta, sem acentos ou espaços especiais.
  const nomeOriginal = formData.get('nome').trim().toUpperCase();
  const turno = formData.get('turno') || 'integral';

  // Verifica seleção de ano e turma.
  const anoSelecionado = form.querySelector('input[name="ano"]:checked');
  const turmaSelecionada = form.querySelector('input[name="turma"]:checked');

  const ano = anoSelecionado ? anoSelecionado.value : "";
  const turma = turmaSelecionada ? turmaSelecionada.value : "";

  // Validação básica dos campos.
  if (!nomeOriginal || !ano || !turma) {
    alert("Preencha todos os campos!");
    bloqueado = false;
    return;
  }

  // Geração de nome de arquivo limpo.
  const nomeArquivo = nomeOriginal.normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\W+/g, "_")
    .replace(/^_+|_+$/g, "");

  const totalFotos = 10;

   // Mostra carregamento.
  if (loader) loader.classList.remove("hidden");
  statusText.innerHTML = '<i class="fas fa-camera mr-1"></i> Iniciando captura de imagens...';

  // Captura em loop.
  for (let i = 1; i <= totalFotos; i++) {
    // Define o tamanho do canvas conforme o vídeo.
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');

    // Ajuste da região central (recorte do rosto)
    const ovalWidth = canvas.width * 0.6;  // Ajustado para 60% da largura
    const ovalHeight = canvas.height * 0.8; // Mantido 80% da altura
    const startX = (canvas.width - ovalWidth) / 2;
    const startY = (canvas.height - ovalHeight) / 2;

    // Criar canvas temporário só para o recorte
    const faceCanvas = document.createElement('canvas');
    faceCanvas.width = ovalWidth;
    faceCanvas.height = ovalHeight;
    const faceCtx = faceCanvas.getContext('2d');

    // Recorte da imagem na área oval (centro do vídeo).
    faceCtx.drawImage(video, startX, startY, ovalWidth, ovalHeight, 0, 0, ovalWidth, ovalHeight);

    // Gera imagem JPEG da captura
    const blob = await new Promise(resolve => faceCanvas.toBlob(resolve, 'image/jpeg', 0.8));
    const imgURL = URL.createObjectURL(blob);
    // Cria e exibe a miniatura da imagem capturada.
    const img = document.createElement('img');
    img.src = imgURL;
    img.classList.add('w-full', 'rounded', 'border');
    previewContainer.appendChild(img);

    // Prepara dados para envio.
    const uploadData = new FormData();
    uploadData.append('foto', blob, `${nomeArquivo}_${i}.jpg`);
    uploadData.append('nome', nomeOriginal);
    uploadData.append('turno', turno);
    uploadData.append('ano', ano);
    uploadData.append('turma', turma);
    uploadData.append('index', i);
    uploadData.append('total', totalFotos);

    // Envia imagem para o backend.
    const resposta = await fetch('/cadastrar_aluno', {
      method: 'POST',
      body: uploadData
    });

    const json = await resposta.json();
    if (!resposta.ok || !json.sucesso) {
      alert(`Erro ao enviar imagem ${i}: ${json.erro || resposta.statusText}`);
      break;
    }

    statusText.innerHTML = `<i class="fas fa-camera mr-1"></i> Captura ${i}/${totalFotos}`;
  }

  // Finaliza.
  statusText.textContent = "";
  if (loader) loader.classList.add("hidden");
  successSound.play();
  mostrarModal();
  desligarWebcam();
  bloqueado = false;
});

// Exibe modal de sucesso com animação.
function mostrarModal() {
  modal.classList.remove("hidden");
  setTimeout(() => {
    modal.classList.add("opacity-100");
    modalContent.classList.remove("scale-95");
    modalContent.classList.add("scale-100");
  }, 10);
}

// Esconde modal com transição.
function esconderModal() {
  modal.classList.remove("opacity-100");
  modalContent.classList.remove("scale-100");
  modalContent.classList.add("scale-95");
  setTimeout(() => {
    modal.classList.add("hidden");
  }, 300);
}

// Botão de repetir cadastro: reseta formulário e oculta modal.
repetirBtn.addEventListener('click', () => {
  form.reset();
  previewContainer.innerHTML = "";
  esconderModal();
});

// Botão de fechar modal manualmente.
fecharModalBtn.addEventListener('click', esconderModal);

// Fecha modal ao clicar fora do conteúdo.
modal.addEventListener('click', (e) => {
  if (e.target === modal) esconderModal();
});

// Fecha modal ao apertar ESC.
window.addEventListener('keydown', (e) => {
  if (e.key === "Escape") esconderModal();
});

// Desliga webcam ao sair da página.
window.addEventListener("beforeunload", desligarWebcam);