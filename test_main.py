from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpar_tarefas():
    """Limpa a lista em memória e reinicia o gerador de ID antes de cada teste."""
    main.tarefas.clear()
    main.proximo_id = 1


def test_criar_tarefa_sucesso():
    payload = {
        "titulo": "Estudar Python",
        "descricao": "Revisar funções e classes",
        "tags": ["python", "estudos"],
    }
    response = client.post("/tarefas", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["titulo"] == "Estudar Python"
    assert data["descricao"] == "Revisar funções e classes"
    assert data["concluida"] is False
    assert data["tags"] == ["python", "estudos"]
    assert "data_criacao" in data
    assert "data_atualizacao" in data


def test_criar_tarefa_dados_invalidos():
    # Título vazio não permitido
    response = client.post("/tarefas", json={"titulo": "", "tags": []})
    assert response.status_code == 422

    # Sem o campo obrigatório título
    response = client.post("/tarefas", json={"descricao": "Sem titulo"})
    assert response.status_code == 422


def test_buscar_tarefa_por_id_sucesso():
    # Criar tarefa
    res_criacao = client.post(
        "/tarefas",
        json={"titulo": "Aprender FastAPI", "descricao": "Rotas e schemas", "tags": ["fastapi"]},
    )
    tarefa_id = res_criacao.json()["id"]

    # Buscar pelo ID
    response = client.get(f"/tarefas/{tarefa_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tarefa_id
    assert data["titulo"] == "Aprender FastAPI"


def test_buscar_tarefa_id_inexistente():
    response = client.get("/tarefas/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Tarefa com ID 999 não encontrada."


def test_buscar_tarefa_id_invalido():
    # ID menor que 1
    response = client.get("/tarefas/0")
    assert response.status_code == 422


def test_atualizar_tarefa_sucesso():
    # Criar tarefa
    res_criacao = client.post(
        "/tarefas",
        json={"titulo": "Estudar FastAPI", "descricao": "Intro", "tags": ["python"]},
    )
    tarefa_criada = res_criacao.json()
    tarefa_id = tarefa_criada["id"]

    # Atualizar tarefa
    payload_atualizacao = {
        "titulo": "Estudar FastAPI Avançado",
        "descricao": "Estudar rotas, parâmetros e respostas",
        "concluida": True,
        "tags": ["python", "fastapi"],
    }
    response = client.put(f"/tarefas/{tarefa_id}", json=payload_atualizacao)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tarefa_id
    assert data["titulo"] == "Estudar FastAPI Avançado"
    assert data["concluida"] is True
    assert data["data_criacao"] == tarefa_criada["data_criacao"]
    assert "data_atualizacao" in data


def test_atualizar_tarefa_inexistente():
    payload = {
        "titulo": "Inexistente",
        "descricao": "",
        "concluida": True,
        "tags": [],
    }
    response = client.put("/tarefas/999", json=payload)
    assert response.status_code == 404


def test_excluir_tarefa_sucesso():
    res = client.post("/tarefas", json={"titulo": "Tarefa para excluir", "tags": []})
    tarefa_id = res.json()["id"]

    # Deletar
    del_res = client.delete(f"/tarefas/{tarefa_id}")
    assert del_res.status_code == 204

    # Verificar que não existe mais
    get_res = client.get(f"/tarefas/{tarefa_id}")
    assert get_res.status_code == 404


def test_excluir_tarefa_inexistente():
    response = client.delete("/tarefas/999")
    assert response.status_code == 404


def test_filtro_por_situacao_concluida():
    # 1 pendente
    client.post("/tarefas", json={"titulo": "Tarefa 1", "tags": []})
    # 1 concluída
    t2 = client.post("/tarefas", json={"titulo": "Tarefa 2", "tags": []}).json()
    client.put(f"/tarefas/{t2['id']}", json={"titulo": "Tarefa 2", "descricao": "", "concluida": True, "tags": []})

    # Filtrar concluida=true
    res_true = client.get("/tarefas?concluida=true")
    assert res_true.status_code == 200
    assert res_true.json()["total"] == 1
    assert res_true.json()["tarefas"][0]["titulo"] == "Tarefa 2"

    # Filtrar concluida=false
    res_false = client.get("/tarefas?concluida=false")
    assert res_false.status_code == 200
    assert res_false.json()["total"] == 1
    assert res_false.json()["tarefas"][0]["titulo"] == "Tarefa 1"


def test_filtro_por_tag():
    client.post("/tarefas", json={"titulo": "Tarefa Python", "tags": ["Python", "Backend"]})
    client.post("/tarefas", json={"titulo": "Tarefa JS", "tags": ["javascript", "frontend"]})

    # Case-insensitive
    res = client.get("/tarefas?tag=python")
    assert res.status_code == 200
    assert res.json()["total"] == 1
    assert res.json()["tarefas"][0]["titulo"] == "Tarefa Python"


def test_filtro_por_titulo():
    client.post("/tarefas", json={"titulo": "Estudar Python básico", "tags": []})
    client.post("/tarefas", json={"titulo": "Exercícios de Python", "tags": []})
    client.post("/tarefas", json={"titulo": "Aprender HTML", "tags": []})

    res = client.get("/tarefas?titulo=python")
    assert res.status_code == 200
    assert res.json()["total"] == 2


def test_ordenacao_asc_desc():
    client.post("/tarefas", json={"titulo": "B - Segunda", "tags": []})
    client.post("/tarefas", json={"titulo": "A - Primeira", "tags": []})
    client.post("/tarefas", json={"titulo": "C - Terceira", "tags": []})

    # Ordenar por titulo ASC
    res_asc = client.get("/tarefas?ordenar_por=titulo&ordem=asc")
    assert res_asc.status_code == 200
    titulos_asc = [t["titulo"] for t in res_asc.json()["tarefas"]]
    assert titulos_asc == ["A - Primeira", "B - Segunda", "C - Terceira"]

    # Ordenar por titulo DESC
    res_desc = client.get("/tarefas?ordenar_por=titulo&ordem=desc")
    assert res_desc.status_code == 200
    titulos_desc = [t["titulo"] for t in res_desc.json()["tarefas"]]
    assert titulos_desc == ["C - Terceira", "B - Segunda", "A - Primeira"]


def test_ordenacao_parametro_invalido():
    response = client.get("/tarefas?ordenar_por=invalido")
    assert response.status_code == 422

    response = client.get("/tarefas?ordem=invalida")
    assert response.status_code == 422


def test_combinacao_filtros():
    client.post("/tarefas", json={"titulo": "Estudar Python", "tags": ["python"]})
    t2 = client.post("/tarefas", json={"titulo": "Revisar Python", "tags": ["python"]}).json()
    client.put(f"/tarefas/{t2['id']}", json={"titulo": "Revisar Python", "descricao": "", "concluida": True, "tags": ["python"]})
    client.post("/tarefas", json={"titulo": "Estudar JavaScript", "tags": ["js"]})

    # Filtrar nao concluida + tag python
    res = client.get("/tarefas?concluida=false&tag=python")
    assert res.status_code == 200
    assert res.json()["total"] == 1
    assert res.json()["tarefas"][0]["titulo"] == "Estudar Python"


def test_paginacao():
    for i in range(1, 16):
        client.post("/tarefas", json={"titulo": f"Tarefa {i:02d}", "tags": []})

    # Pagina 1 limite 5
    res1 = client.get("/tarefas?pagina=1&limite=5")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["pagina"] == 1
    assert data1["limite"] == 5
    assert data1["total"] == 15
    assert len(data1["tarefas"]) == 5
    assert data1["tarefas"][0]["titulo"] == "Tarefa 01"

    # Pagina 2 limite 5
    res2 = client.get("/tarefas?pagina=2&limite=5")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["pagina"] == 2
    assert len(data2["tarefas"]) == 5
    assert data2["tarefas"][0]["titulo"] == "Tarefa 06"


def test_consulta_por_periodo():
    hoje = datetime.now()
    ontem = hoje - timedelta(days=1)
    amanha = hoje + timedelta(days=1)

    client.post("/tarefas", json={"titulo": "Tarefa Hoje", "tags": []})

    data_hoje_str = hoje.strftime("%Y-%m-%d")
    data_ontem_str = ontem.strftime("%Y-%m-%d")
    data_amanha_str = amanha.strftime("%Y-%m-%d")

    # Filtrando intervalo correto
    res = client.get(f"/tarefas?data_inicio={data_ontem_str}&data_fim={data_amanha_str}")
    assert res.status_code == 200
    assert res.json()["total"] == 1

    # Data fim anterior à data inicio
    res_erro = client.get(f"/tarefas?data_inicio={data_amanha_str}&data_fim={data_ontem_str}")
    assert res_erro.status_code == 422
