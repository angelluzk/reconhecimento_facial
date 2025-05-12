const modal = document.getElementById('modal');
const modalAluno = document.getElementById('modalAluno');
const modalTurma = document.getElementById('modalTurma');
const modalTurno = document.getElementById('modalTurno');
const modalData = document.getElementById('modalData');
const modalEntrada = document.getElementById('modalEntrada');
const modalSaida = document.getElementById('modalSaida');
const modalDuracao = document.getElementById('modalDuracao');
const modalStatus = document.getElementById('modalStatus');

function formatarApenasData(data) {
  const dateObj = new Date(data);
  if (isNaN(dateObj.getTime())) return '';

  const dia = String(dateObj.getDate()).padStart(2, '0');
  const mes = String(dateObj.getMonth() + 1).padStart(2, '0');
  const ano = dateObj.getFullYear();

  return `${dia}/${mes}/${ano}`;
}

function formatarHora(data) {
  const dateObj = new Date(data);
  if (isNaN(dateObj.getTime())) return '';

  const horas = String(dateObj.getHours()).padStart(2, '0');
  const minutos = String(dateObj.getMinutes()).padStart(2, '0');
  const segundos = String(dateObj.getSeconds()).padStart(2, '0');

  return `${horas}:${minutos}:${segundos}`;
}

function mostrarDetalhesComDataset(el) {
  const { aluno, turma, turno, data, entrada, saida, duracao, status } = el.dataset;

  modalAluno.textContent = aluno;
  modalTurma.textContent = turma;
  modalTurno.textContent = turno;
  modalData.textContent = data;
  modalEntrada.textContent = entrada;
  modalSaida.textContent = saida;
  modalDuracao.textContent = duracao;
  modalStatus.textContent = status;

  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

function exportarRelatorio(tipo) {
  const urlAtual = new URL(window.location.href);
  const urlBase = `/baixar_relatorio/${tipo}`;
  const queryParams = window.location.search;
  const urlFinal = `${urlBase}${queryParams}`;
  window.location.href = urlFinal;
}

function fecharModal() {
  modal.classList.remove('flex');
  modal.classList.add('hidden');
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') fecharModal();
});

document.getElementById("btnAbrirCadastro").addEventListener("click", function () {
  window.location.href = "/";
});