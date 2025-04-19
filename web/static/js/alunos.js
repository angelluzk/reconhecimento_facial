// Espera o carregamento completo do DOM para executar as funções.
document.addEventListener("DOMContentLoaded", () => {
  carregarAlunos(); // Carrega todos os alunos ao abrir a página.

  // Adiciona evento de envio do formulário do aluno (criar ou editar).
  document.getElementById("formAluno").addEventListener("submit", async (e) => {
    e.preventDefault(); // Evita o recarregamento da página ao enviar o form.

    // Captura os dados dos campos.
    const id = document.getElementById("alunoId").value;
    const nome = document.getElementById("alunoNome").value;
    const turno = document.getElementById("alunoTurno").value;

    // Recupera os valores selecionados de ano e turma.
    const ano = document.querySelector('input[name="ano"]:checked')?.value || "";
    const turma = document.querySelector('input[name="turma"]:checked')?.value || "";

    const turmaCompleta = `${ano} ${turma}`; // Junta os valores (ex: "1º A").
    const payload = { nome, turno, turma: turmaCompleta }; // Dados a serem enviados.

    try {
      // Envia requisição POST (novo) ou PUT (edição) para a API.
      const res = await fetch(`/api/alunos${id ? "/" + id : ""}`, {
        method: id ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        fecharModal();
        carregarAlunos();
        mostrarToast("Aluno(a) salvo com sucesso!");
      } else {
        mostrarToast("Erro ao salvar aluno(a).", "erro");
      }
    } catch (err) {
      console.error("Erro ao salvar aluno(a):", err);
      mostrarToast("Erro ao salvar aluno(a). Tente novamente!", "erro");
    }
  });
});

// Função para abrir o modal com dados preenchidos (editar ou visualizar).
function abrirModal(aluno = null, modo = "editar") {
  // Define o título do modal de acordo com o modo.
  document.getElementById("modalTitulo").innerText =
    modo === "visualizar" ? "Visualizar Aluno" : modo === "editar" ? "Editar Aluno" : "Novo Aluno";

  // Preenche os campos com os dados do aluno(a) ou deixa vazio.
  document.getElementById("alunoId").value = aluno?.id || "";
  document.getElementById("alunoNome").value = aluno?.nome || "";
  document.getElementById("alunoTurno").value = aluno?.turno || "integral";

  // Desmarca todas as opções de ano e turma antes de marcar as corretas.
  document.querySelectorAll('input[name="ano"]').forEach((radio) => (radio.checked = false));
  document.querySelectorAll('input[name="turma"]').forEach((radio) => (radio.checked = false));

  // Se o aluno(a) tiver turma, separa ano e turma e marca os rádios correspondentes.
  if (aluno?.turma) {
    const [ano, turma] = aluno.turma.split(" ");
    const anoRadio = document.querySelector(`input[name="ano"][value="${ano}"]`);
    const turmaRadio = document.querySelector(`input[name="turma"][value="${turma}"]`);
    if (anoRadio) anoRadio.checked = true;
    if (turmaRadio) turmaRadio.checked = true;
  }

  // Se for modo "visualizar", desativa os campos.
  const isVisualizar = modo === "visualizar";
  document.getElementById("alunoNome").disabled = isVisualizar;
  document.getElementById("alunoTurno").disabled = true;
  document.querySelectorAll('input[name="ano"]').forEach((radio) => (radio.disabled = isVisualizar));
  document.querySelectorAll('input[name="turma"]').forEach((radio) => (radio.disabled = isVisualizar));

  // Mostra ou oculta o botão de salvar, dependendo do modo (visualiar ou editar).
  document.getElementById("btnSalvar").classList.toggle("hidden", isVisualizar);
  document.getElementById("btnFechar").innerText = isVisualizar ? "Fechar" : "Cancelar";
  document.getElementById("modalAluno").classList.remove("hidden");
}

// Função para fechar o modal.
function fecharModal() {
  document.getElementById("modalAluno").classList.add("hidden");
}

// Função para carregar os alunos e exibir na tabela.
function carregarAlunos(pagina = 1) {
  const params = new URLSearchParams(window.location.search);

  const nome = params.get("nome") || "";
  const ano = params.get("ano") || "";
  const turma = params.get("turma") || "";

  const tbody = document.getElementById("tabelaAlunos");
  const pagination = document.getElementById("pagination");

  // Mostra um loading animado enquanto carrega os alunos.
  tbody.innerHTML = `
    <tr>
      <td colspan="6" class="text-center py-4">
        <div class="flex justify-center items-center space-x-2">
          <div class="w-4 h-4 bg-blue-500 rounded-full animate-bounce"></div>
          <div class="w-4 h-4 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.1s]"></div>
          <div class="w-4 h-4 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.2s]"></div>
          <span class="ml-3 text-blue-500">Carregando alunos...</span>
        </div>
      </td>
    </tr>`;

  // Faz a requisição à API com filtros e paginação.
  fetch(`/api/alunos?nome=${nome}&ano=${ano}&turma=${turma}&pagina=${pagina}`)
    .then(res => res.json())
    .then(data => {
      const alunos = data.alunos;
      const totalPaginas = data.total_paginas;
      const paginaAtual = data.pagina_atual;

      tbody.innerHTML = ""; // Limpa a tabela para adicionar os novos dados.

      if (alunos.length === 0) {
        // Mostra mensagem se não encontrar alunos.
        tbody.innerHTML = `
          <tr>
            <td colspan="6" class="text-center py-4 text-gray-500">Nenhum aluno encontrado.</td>
          </tr>`;
        return;
      }

      // Monta a linha da tabela para cada aluno.
      alunos.forEach((aluno) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="px-4 py-2">${aluno.id}</td>
          <td class="px-4 py-2">${aluno.nome}</td>
          <td class="px-4 py-2">${aluno.turno}</td>
          <td class="px-4 py-2">${aluno.turma}</td>
          <td class="px-4 py-2">
            <img src="/fotos_alunos/${aluno.foto}" alt="Foto" class="w-10 h-10 rounded-full object-cover" />
          </td>
          <td class="px-4 py-2">
            <button onclick='abrirModal(${JSON.stringify(aluno)}, "editar")' class="text-blue-600 hover:text-blue-800 mr-2"><i class="fas fa-edit"></i> Alterar</button>
            <button onclick='abrirModal(${JSON.stringify(aluno)}, "visualizar")' class="text-green-600 hover:text-green-800 mr-2"><i class="fas fa-eye"></i> Visualizar</button>
            <button onclick='deletarAluno(${aluno.id})' class="text-red-600 hover:text-red-800"><i class="fas fa-trash"></i> Deletar</button>
          </td>
        `;
        tbody.appendChild(tr); // Adiciona à tabela.
      });

      // Atualizar a paginação
      pagination.innerHTML = `
        ${paginaAtual > 1 ? `<a href="#" onclick="carregarAlunos(${paginaAtual - 1})" class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md">Anterior</a>` : ''}
        <span class="py-2 px-4 text-gray-700">Página ${paginaAtual} de ${totalPaginas}</span>
        ${paginaAtual < totalPaginas ? `<a href="#" onclick="carregarAlunos(${paginaAtual + 1})" class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md">Próxima</a>` : ''}
      `;
    })
    .catch(err => {
      console.error("Erro ao carregar alunos:", err);
      mostrarToast("Erro ao carregar alunos. Tente novamente!", "erro");
    });
}

// Função para deletar aluno(a) após confirmação.
async function deletarAluno(id) {
  if (!confirm("Deseja realmente deletar este aluno(a)?")) return;
  try {
    const res = await fetch(`/api/alunos/${id}`, { method: "DELETE" });
    if (res.ok) {
      carregarAlunos(); // Atualiza a lista.
      mostrarToast("Aluno(a) excluído com sucesso!");
    } else {
      mostrarToast("Erro ao excluir aluno(a).", "erro");
    }
  } catch (err) {
    console.error("Erro ao deletar aluno(a):", err);
    mostrarToast("Erro ao excluir aluno(a). Tente novamente!", "erro");
  }
}

// Função de alerta (tipo toast) no centro da tela.
function mostrarToast(mensagem) {
  const toast = document.getElementById("toast");
  const content = document.getElementById("toastContent");

  content.textContent = mensagem;
  content.classList.remove("opacity-0");
  content.classList.add("opacity-100");

  setTimeout(() => {
    content.classList.remove("opacity-100");
    content.classList.add("opacity-0");
  }, 3000);
}