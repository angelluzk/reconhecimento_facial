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
const botaoTrocarCamera = document.getElementById('botao-trocar-camera');
const fecharModalBtn = document.getElementById('fecharModal');

let stream = null;
let webcamLigada = false;
let bloqueado = false;
let cameraFrontal = true;

async function ligarWebcam() {
  if (stream) desligarWebcam();
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: cameraFrontal ? "user" : "environment"
      }
    });
    video.srcObject = stream;
    video.classList.remove("hidden");
    botaoWebcam.innerHTML = '<i class="fas fa-stop mr-1"></i> Desligar Webcam';
    webcamLigada = true;
  } catch (error) {
    statusText.textContent = "Erro ao acessar a câmera: " + error.message;
  }
}

function desligarWebcam() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
  video.classList.add("hidden");
  video.srcObject = null;
  webcamLigada = false;
  botaoWebcam.innerHTML = '<i class="fas fa-play mr-1"></i> Ligar Webcam';
}

botaoWebcam.addEventListener("click", () => {
  webcamLigada ? desligarWebcam() : ligarWebcam();
});

botaoTrocarCamera.addEventListener("click", () => {
  cameraFrontal = !cameraFrontal;
  if (webcamLigada) ligarWebcam();
});

navigator.mediaDevices.enumerateDevices().then(devices => {
  const cameras = devices.filter(device => device.kind === 'videoinput');
  if (cameras.length <= 1) {
    botaoTrocarCamera.classList.add('hidden');
  }
});

form.addEventListener('submit', async e => {
  e.preventDefault();
  if (bloqueado) return;
  bloqueado = true;

  if (!webcamLigada) {
    alert("Ligue a webcam antes de iniciar a captura!!");
    bloqueado = false;
    return;
  }

  previewContainer.innerHTML = "";
  const formData = new FormData(form);
  const nomeOriginal = formData.get('nome').trim();
  const turno = formData.get('turno') || 'integral';
  const turma = formData.get('turma');

  if (!nomeOriginal || !turma) {
    alert("Preencha todos os campos!!");
    bloqueado = false;
    return;
  }

  const nomeArquivo = nomeOriginal.normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\W+/g, "_")
    .replace(/^_+|_+$/g, "");

  statusText.textContent = "📸 Iniciando captura de imagens...";
  const totalFotos = 10;

  for (let i = 1; i <= totalFotos; i++) {
    await new Promise(r => setTimeout(r, 500));
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
    const imgURL = URL.createObjectURL(blob);
    const img = document.createElement('img');
    img.src = imgURL;
    img.classList.add('w-full', 'rounded', 'border');
    previewContainer.appendChild(img);

    const uploadData = new FormData();
    uploadData.append('foto', blob, `${nomeArquivo}_${i}.jpg`);
    uploadData.append('nome', nomeOriginal);
    uploadData.append('turno', turno); 
    uploadData.append('turma', turma);
    uploadData.append('index', i);
    uploadData.append('total', totalFotos);

    await fetch('/cadastrar_aluno', {
      method: 'POST',
      body: uploadData
    });

    statusText.textContent = `📷 Captura ${i}/${totalFotos}`;
  }

  statusText.textContent = "";
  successSound.play();
  mostrarModal();
  desligarWebcam();
  bloqueado = false;
});

function mostrarModal() {
  modal.classList.remove("hidden");
  setTimeout(() => {
    modal.classList.add("opacity-100");
    modalContent.classList.remove("scale-95");
    modalContent.classList.add("scale-100");
  }, 10);
}

function esconderModal() {
  modal.classList.remove("opacity-100");
  modalContent.classList.remove("scale-100");
  modalContent.classList.add("scale-95");
  setTimeout(() => {
    modal.classList.add("hidden");
  }, 300);
}

repetirBtn.addEventListener('click', () => {
  form.reset();
  previewContainer.innerHTML = "";
  esconderModal();
});

fecharModalBtn.addEventListener('click', esconderModal);

modal.addEventListener('click', (e) => {
  if (e.target === modal) esconderModal();
});

window.addEventListener('keydown', (e) => {
  if (e.key === "Escape") esconderModal();
});

window.addEventListener("beforeunload", desligarWebcam);
