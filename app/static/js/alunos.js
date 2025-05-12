document.addEventListener("DOMContentLoaded", () => {
  carregarAlunos();

  document.getElementById("formAluno").addEventListener("submit", async (e) => {
    e.preventDefault();

    const id = document.getElementById("alunoId").value;
    let nome = document.getElementById("alunoNome").value;

    const nomeFormatado = restaurarAcentos(nome.replace(/_/g, ' '));

    const turno = document.getElementById("alunoTurno").value;
    const ano = document.querySelector('input[name="ano"]:checked')?.value || "";
    const turma = document.querySelector('input[name="turma"]:checked')?.value || "";

    const turmaCompleta = `${ano} ${turma}`.trim();
    const payload = { nome: nomeFormatado, turno, turma: turmaCompleta, ano, turma };

    try {
      const res = await fetch(`/alunos/api/alunos${id ? "/" + id : ""}`, {
        method: id ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        fecharModal();
        const paginaAtual = getPaginaAtual();
        carregarAlunos(paginaAtual);
        mostrarToast("Aluno salvo com sucesso!");
      } else {
        mostrarToast("Erro ao salvar aluno.", "erro");
      }
    } catch (err) {
      console.error("Erro ao salvar aluno:", err);
      mostrarToast("Erro ao salvar aluno. Tente novamente!", "erro");
    }
  });

  document.getElementById("btnFechar").addEventListener("click", fecharModal);
});

function restaurarAcentos(nome) {
  return nome.normalize('NFC');
}


function abrirModal(aluno = null, modo = "editar") {
  document.getElementById("modalTitulo").innerText =
    modo === "visualizar" ? "Visualizar Aluno(a)" : modo === "editar" ? "Editar Dados do Aluno" : "Novo Aluno";

  document.getElementById("alunoId").value = aluno?.id || "";
  document.getElementById("alunoNome").value = aluno?.nome || "";
  document.getElementById("alunoTurno").value = aluno?.turno || "integral";

  document.querySelectorAll('input[name="ano"]').forEach((radio) => (radio.checked = false));
  document.querySelectorAll('input[name="turma"]').forEach((radio) => (radio.checked = false));

  if (aluno?.turma) {
    const [ano, turma] = aluno.turma.split(" ");
    const anoRadio = document.querySelector(`input[name="ano"][value="${ano}"]`);
    const turmaRadio = document.querySelector(`input[name="turma"][value="${turma}"]`);
    if (anoRadio) anoRadio.checked = true;
    if (turmaRadio) turmaRadio.checked = true;
  }

  const isVisualizar = modo === "visualizar";

  document.getElementById("alunoNome").disabled = isVisualizar;
  document.getElementById("alunoTurno").disabled = true;

  document.querySelectorAll('input[name="ano"]').forEach((radio) => (radio.disabled = isVisualizar));
  document.querySelectorAll('input[name="turma"]').forEach((radio) => (radio.disabled = isVisualizar));

  document.getElementById("btnSalvar").classList.toggle("hidden", isVisualizar);
  document.getElementById("btnFechar").innerText = isVisualizar ? "Fechar" : "Cancelar";

  document.getElementById("modalAluno").classList.remove("hidden");
}

function fecharModal() {
  document.getElementById("modalAluno").classList.add("hidden");
}

function getPaginaAtual() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get("pagina") || 1;
}

function carregarAlunos(pagina = 1) {
  const params = new URLSearchParams(window.location.search);

  const nome = params.get("nome") || "";
  const ano = params.get("ano") || "";
  const turma = params.get("turma") || "";

  const tbody = document.getElementById("tabelaAlunos");
  const pagination = document.getElementById("pagination");

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

  fetch(`/alunos/api/alunos?nome=${nome}&ano=${ano}&turma=${turma}&pagina=${pagina}`)
    .then(res => res.json())
    .then(data => {
      const alunos = data.alunos;
      const totalPaginas = data.total_paginas;
      const paginaAtual = data.pagina_atual;

      tbody.innerHTML = "";

      if (alunos.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="6" class="text-center py-4 text-gray-500">Nenhum aluno encontrado.</td>
          </tr>`;
        return;
      }

      alunos.forEach((aluno) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="px-4 py-2">${aluno.id}</td>
          <td class="px-4 py-2">${aluno.nome}</td>
          <td class="px-4 py-2">${aluno.turno}</td>
          <td class="px-4 py-2">${aluno.turma}</td>
          <td class="px-4 py-2">
            <img src="/alunos/fotos_alunos/${aluno.foto}" alt="Foto" class="w-10 h-10 rounded-full object-cover" />
          </td>
          <td class="px-4 py-2">
            <button onclick='abrirModal(${JSON.stringify(aluno)}, "editar")' class="text-blue-600 hover:text-blue-800 mr-2"><i class="fas fa-edit"></i> Alterar</button>
            <button onclick='abrirModal(${JSON.stringify(aluno)}, "visualizar")' class="text-green-600 hover:text-green-800 mr-2"><i class="fas fa-eye"></i> Visualizar</button>
            <button onclick='deletarAluno(${aluno.id}, ${paginaAtual})' class="text-red-600 hover:text-red-800"><i class="fas fa-trash"></i> Deletar</button>
          </td>
        `;
        tbody.appendChild(tr);
      });

      pagination.innerHTML = `
      <div class="flex flex-wrap justify-center gap-2">
        ${paginaAtual > 1 ? `<a href="#" onclick="carregarAlunos(1)" class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md"><< Primeira</a>` : ''}
        ${paginaAtual > 1 ? `<a href="#" onclick="carregarAlunos(${paginaAtual - 1})" class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md">Anterior</a>` : ''}
        <span class="py-2 px-4 text-gray-700">Página ${paginaAtual} de ${totalPaginas}</span>
        ${paginaAtual < totalPaginas ? `<a href="#" onclick="carregarAlunos(${paginaAtual + 1})" class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md">Próxima</a>` : ''}
        ${paginaAtual < totalPaginas ? `<a href="#" onclick="carregarAlunos(${totalPaginas})" class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md">Última >></a>` : ''}
      </div>
    `;

      const url = new URL(window.location);
      url.searchParams.set("pagina", paginaAtual);
      window.history.pushState({}, "", url);
    })
    .catch(err => {
      console.error("Erro ao carregar alunos:", err);
      mostrarToast("Erro ao carregar alunos. Tente novamente!", "erro");
    });
}

async function deletarAluno(id, paginaAtual) {
  if (!confirm("Deseja realmente deletar este aluno(a)?")) return;
  try {
    const res = await fetch(`/alunos/api/alunos/${id}`, { method: "DELETE" });
    if (res.ok) {
      carregarAlunos(paginaAtual);
      mostrarToast("Aluno excluído com sucesso!");
    } else {
      mostrarToast("Erro ao excluir aluno.", "erro");
    }
  } catch (err) {
    console.error("Erro ao deletar aluno:", err);
    mostrarToast("Erro ao excluir aluno. Tente novamente!", "erro");
  }
}

function mostrarToast(mensagem, isError = false) {
  const toast = document.getElementById("toast");
  const toastContent = document.getElementById("toastContent");
  toastContent.textContent = mensagem;

  toastContent.classList.remove("bg-green-500", "bg-red-500");

  toastContent.classList.add(isError ? "bg-red-500" : "bg-green-500");

  toastContent.classList.add("opacity-100");

  setTimeout(() => {
    toastContent.classList.remove("opacity-100");
  }, 3000);
}