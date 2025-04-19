// Função que mostra o modal com os detalhes de presença do aluno ao clicar em um item da lista.
function mostrarDetalhesComDataset(el) {
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