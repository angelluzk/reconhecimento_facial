document.addEventListener("DOMContentLoaded", () => {
  carregarAlunos();

  document.getElementById("formAluno").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("alunoId").value;
    const nome = document.getElementById("alunoNome").value;
    const turno = document.getElementById("alunoTurno").value;

    const ano = document.querySelector('input[name="ano"]:checked')?.value || "";
    const turma = document.querySelector('input[name="turma"]:checked')?.value || "";

 const turmaCompleta = `${ano} ${turma}`;

 const payload = { nome, turno, turma: turmaCompleta };

    try {
      const res = await fetch(`/api/alunos${id ? "/" + id : ""}`, {
        method: id ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        fecharModal();
        carregarAlunos();
        alert("Aluno(a) salvo com sucesso!");
      } else {
        alert("Erro ao salvar aluno(a).");
      }
    } catch (err) {
      console.error("Erro ao salvar aluno(a):", err);
      alert("Erro ao salvar aluno(a). Tente novamente!");
    }
  });
});

function abrirModal(aluno = null, modo = 'editar') {
  document.getElementById("modalTitulo").innerText = modo === 'visualizar' ? "Visualizar Aluno" : modo === 'editar' ? "Editar Aluno" : "Novo Aluno";
  document.getElementById("alunoId").value = aluno?.id || "";
  document.getElementById("alunoNome").value = aluno?.nome || "";
  document.getElementById("alunoTurno").value = aluno?.turno || "integral";
   document.querySelectorAll('input[name="ano"]').forEach(radio => {
    radio.checked = false;
  });
  document.querySelectorAll('input[name="turma"]').forEach(radio => {
    radio.checked = false;
  });

  if (aluno?.turma) {
    const [ano, turma] = aluno.turma.split(" ");
    const anoRadio = document.querySelector(`input[name="ano"][value="${ano}"]`);
    const turmaRadio = document.querySelector(`input[name="turma"][value="${turma}"]`);

    if (anoRadio) anoRadio.checked = true;
    if (turmaRadio) turmaRadio.checked = true;
  }

  const isVisualizar = modo === 'visualizar';
  document.getElementById("alunoNome").disabled = isVisualizar;
  document.getElementById("alunoTurno").disabled = true;
  document.querySelectorAll('input[name="ano"]').forEach(radio => {
    radio.disabled = isVisualizar;
  });
  document.querySelectorAll('input[name="turma"]').forEach(radio => {
    radio.disabled = isVisualizar;
  });

  if (isVisualizar) {
    document.getElementById("btnSalvar").classList.add("hidden");
    document.getElementById("btnFechar").innerText = "Fechar";
  } else {
    document.getElementById("btnSalvar").classList.remove("hidden");
    document.getElementById("btnFechar").innerText = "Cancelar";
  }

  document.getElementById("modalAluno").classList.remove("hidden");
}

function fecharModal() {
  document.getElementById("modalAluno").classList.add("hidden");
}

async function carregarAlunos() {
  try {
    const res = await fetch("/api/alunos");
    const alunos = await res.json();

    const tbody = document.getElementById("tabelaAlunos");
    tbody.innerHTML = "";

    alunos.forEach(aluno => {
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
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Erro ao carregar alunos:", err);
    alert("Erro ao carregar alunos. Tente novamente!");
  }
}

async function deletarAluno(id) {
  if (!confirm("Deseja realmente deletar este aluno(a)?")) return;
  try {
    const res = await fetch(`/api/alunos/${id}`, { method: "DELETE" });
    if (res.ok) {
      carregarAlunos();
      alert("Aluno(a) excluído com sucesso!");
    } else {
      alert("Erro ao excluir aluno(a).");
    }
  } catch (err) {
    console.error("Erro ao deletar aluno(a):", err);
    alert("Erro ao excluir aluno(a). Tente novamente!");
  }
}