document.addEventListener("DOMContentLoaded", function () {
  const video = document.getElementById('video');
  const canvas = document.getElementById('canvas');
  const form = document.getElementById('cadastro-form');
  const statusText = document.getElementById('status');
  const previewContainer = document.getElementById('preview-container');
  const botaoWebcam = document.getElementById('botao-webcam');
  const botaoCaptura = document.getElementById('botao-captura');
  const loader = document.getElementById('loader');
  const userIcon = document.getElementById('user-icon');
  const userMenu = document.getElementById('user-menu');
  const logoutButton = document.getElementById('btnLogout');

  let stream = null;
  let webcamLigada = false;
  let bloqueado = false;
  let cameraFrontal = true;

  async function verificarWebcam() {
    if (!navigator.mediaDevices?.getUserMedia) {
      alert("Seu navegador não suporta acesso à câmera.");
      return false;
    }
    return true;
  }

  async function ligarWebcam() {
    desligarWebcam();
    if (!await verificarWebcam()) return;

    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: cameraFrontal ? "user" : "environment" }
      });
      video.srcObject = stream;
      video.classList.remove("hidden");
      document.getElementById('filtro')?.classList.remove("hidden");
      botaoWebcam.innerHTML = '<i class="fas fa-stop mr-1"></i> Desligar Webcam';
      webcamLigada = true;
    } catch (error) {
      statusText.textContent = "Erro ao acessar a câmera: " + error.message;
    }
  }

  function desligarWebcam() {
    stream?.getTracks().forEach(track => track.stop());
    stream = null;
    video.srcObject = null;
    video.classList.add("hidden");
    document.getElementById('filtro')?.classList.add("hidden");
    botaoWebcam.innerHTML = '<i class="fas fa-play mr-1"></i> Ligar Webcam';
    webcamLigada = false;
  }

  async function enviarImagem(blob, nomeArquivo, turno, ano, turma, i, total) {
    const data = new FormData();
    data.append('foto', blob, `${nomeArquivo}_${i}.jpg`);
    data.append('nome', nomeArquivo);
    data.append('turno', turno);
    data.append('ano', ano);
    data.append('turma', turma);
    data.append('index', i);
    data.append('total', total);

    const response = await fetch('/alunos/cadastrar_aluno', {
      method: 'POST',
      body: data
    });

    return await response.json();
  }

  async function capturarFotos(nomeArquivo, turno, ano, turma) {
    const totalFotos = 10;
    previewContainer.innerHTML = "";
    loader?.classList.remove("hidden");
    statusText.innerHTML = '<i class="fas fa-camera mr-1"></i> Iniciando captura...';

    for (let i = 1; i <= totalFotos; i++) {
      await new Promise(r => setTimeout(r, 100));

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');

      const ovalWidth = canvas.width * 0.6;
      const ovalHeight = canvas.height * 0.8;
      const startX = (canvas.width - ovalWidth) / 2;
      const startY = (canvas.height - ovalHeight) / 2;

      const faceCanvas = document.createElement('canvas');
      faceCanvas.width = ovalWidth;
      faceCanvas.height = ovalHeight;
      faceCanvas.getContext('2d').drawImage(video, startX, startY, ovalWidth, ovalHeight, 0, 0, ovalWidth, ovalHeight);

      const blob = await new Promise(res => faceCanvas.toBlob(res, 'image/jpeg', 0.8));
      const img = document.createElement('img');
      img.src = URL.createObjectURL(blob);
      img.className = 'rounded-lg border border-gray-300 shadow w-full';
      previewContainer.appendChild(img);

      const resultado = await enviarImagem(blob, nomeArquivo, turno, ano, turma, i, totalFotos);
      if (!resultado.sucesso) {
        alert(`Erro na imagem ${i}: ${resultado.erro || "Erro desconhecido"}`);
        break;
      }

      statusText.innerHTML = `<i class="fas fa-camera mr-1"></i> Captura ${i}/${totalFotos}`;
    }

    loader?.classList.add("hidden");
    statusText.textContent = "";
    successSound?.play();
    mostrarModal();
    desligarWebcam();
    bloqueado = false;
  }

  botaoWebcam.addEventListener("click", () => {
    webcamLigada ? desligarWebcam() : ligarWebcam();
  });

  botaoCaptura.addEventListener('click', async e => {
    e.preventDefault();
    if (bloqueado || !webcamLigada) return alert("Ligue a webcam antes de iniciar a captura!");
    bloqueado = true;

    const formData = new FormData(form);
    const nome = formData.get('nome')?.trim().toUpperCase();
    const turno = formData.get('turno') || 'integral';
    const ano = form.querySelector('input[name="ano"]:checked')?.value;
    const turma = form.querySelector('input[name="turma"]:checked')?.value;

    if (!nome || !ano || !turma) {
      alert("Preencha todos os campos!");
      bloqueado = false;
      return;
    }

    const nomeArquivo = nome.trim().toUpperCase()
      .replace(/[^a-zA-ZÀ-Úà-ú\s]/g, "");

    await capturarFotos(nomeArquivo, turno, ano, turma);
  });

  window.addEventListener("beforeunload", desligarWebcam);

  document.getElementById("anoAtual").textContent = new Date().getFullYear();

  userIcon.addEventListener('click', () => {
    userMenu.classList.toggle('hidden');
  });

  document.addEventListener('click', (e) => {
    if (!userMenu.contains(e.target) && !userIcon.contains(e.target)) {
      userMenu.classList.add('hidden');
    }
  });

  logoutButton?.addEventListener('click', () => {
    window.location.href = '/logout';
  });
});