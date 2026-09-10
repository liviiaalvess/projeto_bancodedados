function preencherFormularioEdicao(cliente) {
  document.getElementById('nome').value = cliente.nome
  document.getElementById('cpf').value = cliente.cpf
  document.getElementById('telefone').value = cliente.telefone || ''
  document.getElementById('cidade').value = cliente.cidade || ''
  document.getElementById('uf').value = cliente.uf || ''

  formCliente.dataset.idCliente = cliente.idcliente
  botaoSubmit.textContent = 'Salvar alteração'
  botaoSubmit.classList.remove('btn-primary')
  botaoSubmit.classList.add('btn-success')
}

async function deletarCliente(id) {
  if (!confirm('Tem certeza que deseja excluir este cliente?')) return

  await fetch(`${API}/clientes/${id}`, { method: 'DELETE' })
  listarClientes()
}