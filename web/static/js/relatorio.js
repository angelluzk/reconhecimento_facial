function mostrarDetalhesComDataset(el) {
    document.getElementById('modalAluno').textContent = el.dataset.aluno;
    document.getElementById('modalTurma').textContent = el.dataset.turma;
    document.getElementById('modalTurno').textContent = el.dataset.turno;
    document.getElementById('modalData').textContent = el.dataset.data;
    document.getElementById('modalEntrada').textContent = el.dataset.entrada;
    document.getElementById('modalSaida').textContent = el.dataset.saida;
    document.getElementById('modalDuracao').textContent = el.dataset.duracao;
    document.getElementById('modal').classList.remove('hidden');
    document.getElementById('modal').classList.add('flex');
  }
  
  function fecharModal() {
    document.getElementById('modal').classList.remove('flex');
    document.getElementById('modal').classList.add('hidden');
  }
  
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') fecharModal();
  });  