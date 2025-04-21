// Função para formatar a data no formato dd/mm/yyyy.
function formatarApenasData(data) {
  const dateObj = new Date(data);

  if (isNaN(dateObj.getTime())) {
    return '';
  }

  const dia = String(dateObj.getDate()).padStart(2, '0');
  const mes = String(dateObj.getMonth() + 1).padStart(2, '0');
  const ano = dateObj.getFullYear();

  return `${dia}/${mes}/${ano}`;
}

// Função para formatar a hora no formato hh:mm:ss.
function formatarHora(data) {
  const dateObj = new Date(data); // Utiliza a data completa fornecida com a data correta.

  if (isNaN(dateObj.getTime())) {
    return '';
  }

  const horas = String(dateObj.getHours()).padStart(2, '0');
  const minutos = String(dateObj.getMinutes()).padStart(2, '0');
  const segundos = String(dateObj.getSeconds()).padStart(2, '0');

  return `${horas}:${minutos}:${segundos}`;
}

// Função que mostra o modal com os detalhes de presença do aluno ao clicar em um item da lista.
function mostrarDetalhesComDataset(el) {
  console.log(el.dataset);
  // Verifica se o modal existe na página.
  if (document.getElementById('modal')) {
    // Preenche os campos do modal com os dados armazenados nos atributos data-* do elemento clicado.
    document.getElementById('modalAluno').textContent = el.dataset.aluno;
    document.getElementById('modalTurma').textContent = el.dataset.turma;
    document.getElementById('modalTurno').textContent = el.dataset.turno;
    document.getElementById('modalData').textContent = el.dataset.data;
    document.getElementById('modalEntrada').textContent = el.dataset.entrada;
    document.getElementById('modalSaida').textContent = el.dataset.saida;
    document.getElementById('modalDuracao').textContent = el.dataset.duracao;
    document.getElementById('modalStatus').textContent = el.dataset.status;

    // Exibe o modal trocando as classes (usando Tailwind: "hidden" → invisível, "flex" → visível).
    document.getElementById('modal').classList.remove('hidden');
    document.getElementById('modal').classList.add('flex');
  }
}

// Função para fechar o modal ocultando ele (troca classe "flex" por "hidden").
function fecharModal() {
  document.getElementById('modal').classList.remove('flex');
  document.getElementById('modal').classList.add('hidden');
}

// Permite fechar o modal pressionando a tecla ESC no teclado.
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') fecharModal();
});