
import pytest
from fastapi.testclient import TestClient
import main


@pytest.fixture
def client():
    """Cria o cliente para testar a API."""
    return TestClient(main.app)


@pytest.fixture(autouse=True)
def limpar_tarefas():
    """Limpa as tarefas antes de cada teste."""
    main.tarefas.clear()
    main.proximo_id = 1


@pytest.fixture
def tarefas_cadastradas(client):
    """Cadastra tarefas de exemplo para reutilizar nos testes."""
    tarefas = [
        {
            "titulo": "Estudar Python",
            "descricao": "Revisar FastAPI",
            "tags": ["python", "estudo"]
        },
        {
            "titulo": "Estudar banco de dados",
            "descricao": "Revisar SQL",
            "tags": ["banco", "estudo"]
        },
        {
            "titulo": "Fazer atividade",
            "descricao": "Concluir exercícios",
            "tags": ["python", "atividade"]
        }
    ]

    cadastradas = []

    for tarefa in tarefas:
        resposta = client.post("/tarefas", json=tarefa)
        cadastradas.append(resposta.json())

    return cadastradas
