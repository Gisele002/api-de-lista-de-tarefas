
import time
import pytest


# ==========================================
# 1. TESTES DE CRIAÇÃO E CAMPOS OBRIGATÓRIOS
# ==========================================

def test_listar_tarefas_vazio(client):
    response = client.get("/tarefas")

    assert response.status_code == 200
    assert response.json()["tarefas"] == []
    assert response.json()["total"] == 0


def test_criar_tarefa_com_campos_obrigatorios(client):
    response = client.post(
        "/tarefas",
        json={
            "titulo": "Estudar Python",
            "descricao": "Revisar FastAPI",
            "tags": ["python", "estudo"],
        },
    )

    assert response.status_code == 201

    tarefa = response.json()

    campos_obrigatorios = [
        "id",
        "titulo",
        "descricao",
        "concluida",
        "tags",
        "data_criacao",
        "data_atualizacao",
    ]

    for campo in campos_obrigatorios:
        assert campo in tarefa

    assert tarefa["concluida"] is False
    assert tarefa["tags"] == ["python", "estudo"]
    assert tarefa["data_criacao"]
    assert tarefa["data_atualizacao"]


def test_ids_gerados_automaticamente(client):
    primeira = client.post(
        "/tarefas",
        json={"titulo": "Primeira", "tags": []},
    ).json()

    segunda = client.post(
        "/tarefas",
        json={"titulo": "Segunda", "tags": []},
    ).json()

    assert primeira["id"] == 1
    assert segunda["id"] == 2


def test_rejeitar_tarefa_sem_titulo(client):
    response = client.post(
        "/tarefas",
        json={"descricao": "Sem título", "tags": []},
    )

    assert response.status_code == 422


def test_rejeitar_tags_com_tipo_invalido(client):
    response = client.post(
        "/tarefas",
        json={"titulo": "Tarefa inválida", "tags": "python"},
    )

    assert response.status_code == 422


def test_rejeitar_titulo_com_tipo_invalido(client):
    response = client.post(
        "/tarefas",
        json={"titulo": 123},
    )

    assert response.status_code == 422


# ==========================================
# 2. TESTES DE LISTAGEM
# ==========================================

def test_listar_todas_as_tarefas(client, tarefas_cadastradas):
    response = client.get("/tarefas")

    assert response.status_code == 200

    dados = response.json()

    assert dados["total"] == len(tarefas_cadastradas)
    assert len(dados["tarefas"]) == 3


def test_listagem_contem_campos_obrigatorios(
    client, tarefas_cadastradas
):
    response = client.get("/tarefas")

    assert response.status_code == 200

    campos_obrigatorios = [
        "id",
        "titulo",
        "descricao",
        "concluida",
        "tags",
        "data_criacao",
        "data_atualizacao",
    ]

    for tarefa in response.json()["tarefas"]:
        for campo in campos_obrigatorios:
            assert campo in tarefa


# ==========================================
# 3. TESTES DE ATUALIZAÇÃO
# ==========================================

def test_atualizar_tarefa_com_sucesso(client):
    tarefa = client.post(
        "/tarefas",
        json={"titulo": "Original", "descricao": "Antiga", "tags": []},
    ).json()

    time.sleep(0.01)

    response = client.put(
        f"/tarefas/{tarefa['id']}",
        json={
            "titulo": "Atualizada",
            "descricao": "Nova descrição",
            "concluida": True,
            "tags": ["python", "teste"],
        },
    )

    assert response.status_code == 200

    atualizada = response.json()

    assert atualizada["titulo"] == "Atualizada"
    assert atualizada["descricao"] == "Nova descrição"
    assert atualizada["concluida"] is True
    assert atualizada["tags"] == ["python", "teste"]


def test_atualizacao_preserva_data_criacao_e_altera_data_atualizacao(
    client,
):
    tarefa = client.post(
        "/tarefas",
        json={"titulo": "Original", "tags": []},
    ).json()

    data_criacao_original = tarefa["data_criacao"]
    data_atualizacao_original = tarefa["data_atualizacao"]

    time.sleep(0.01)

    response = client.put(
        f"/tarefas/{tarefa['id']}",
        json={
            "titulo": "Atualizada",
            "descricao": "",
            "concluida": True,
            "tags": [],
        },
    )

    assert response.status_code == 200

    atualizada = response.json()

    assert atualizada["data_criacao"] == data_criacao_original
    assert atualizada["data_atualizacao"] != data_atualizacao_original


def test_atualizar_tarefa_inexistente(client):
    response = client.put(
        "/tarefas/999",
        json={
            "titulo": "Atualizada",
            "descricao": "",
            "concluida": True,
            "tags": [],
        },
    )

    assert response.status_code == 404


# ==========================================
# 4. TESTES DE EXCLUSÃO
# ==========================================

def test_excluir_tarefa_remove_da_listagem(client):
    tarefa = client.post(
        "/tarefas",
        json={"titulo": "Excluir", "tags": []},
    ).json()

    response = client.delete(f"/tarefas/{tarefa['id']}")

    assert response.status_code == 204

    listagem = client.get("/tarefas")

    assert listagem.json()["tarefas"] == []


def test_buscar_tarefa_excluida_retorna_404(client):
    tarefa = client.post(
        "/tarefas",
        json={"titulo": "Excluir", "tags": []},
    ).json()

    client.delete(f"/tarefas/{tarefa['id']}")

    response = client.get(f"/tarefas/{tarefa['id']}")

    assert response.status_code == 404


def test_excluir_tarefa_inexistente(client):
    response = client.delete("/tarefas/999")

    assert response.status_code == 404


# ==========================================
# 5. TESTES DE FILTROS SEM RESULTADOS
# ==========================================

@pytest.mark.parametrize(
    "parametro",
    [
        "concluida=true",
        "concluida=false",
        "tag=naoexiste",
        "titulo=naoexiste",
    ],
)
def test_filtros_sem_resultados(client, parametro):
    tarefa = client.post(
        "/tarefas",
        json={"titulo": "Estudar Python", "tags": ["python"]},
    ).json()

    if parametro == "concluida=false":
        client.put(
            f"/tarefas/{tarefa['id']}",
            json={
                "titulo": "Estudar Python",
                "descricao": "",
                "concluida": True,
                "tags": ["python"],
            },
        )

    response = client.get(f"/tarefas?{parametro}")

    assert response.status_code == 200
    assert response.json()["tarefas"] == []
    assert response.json()["total"] == 0


# ==========================================
# 6. TESTES DE ORDENAÇÃO
# ==========================================

@pytest.mark.parametrize(
    "campo",
    ["id", "titulo", "data_criacao", "data_atualizacao"],
)
@pytest.mark.parametrize("ordem", ["asc", "desc"])
def test_ordenacao_por_todos_os_campos(
    client, campo, ordem
):
    tarefas = []

    for titulo in ["Tarefa C", "Tarefa A", "Tarefa B"]:
        tarefa = client.post(
            "/tarefas",
            json={"titulo": titulo, "tags": []},
        ).json()

        tarefas.append(tarefa)

        if campo == "data_atualizacao":
            time.sleep(0.01)

            atualizada = client.put(
                f"/tarefas/{tarefa['id']}",
                json={
                    "titulo": titulo,
                    "descricao": "",
                    "concluida": True,
                    "tags": [],
                },
            ).json()

            tarefas[-1] = atualizada

        if campo == "data_criacao":
            time.sleep(0.01)

    response = client.get(
        f"/tarefas?ordenar_por={campo}&ordem={ordem}"
    )

    assert response.status_code == 200

    resultado = response.json()["tarefas"]

    esperado = sorted(
        tarefas,
        key=lambda tarefa: tarefa[campo],
        reverse=(ordem == "desc"),
    )

    assert [t[campo] for t in resultado] == [
        t[campo] for t in esperado
    ]


# ==========================================
# 7. TESTES DE FILTROS COMBINADOS
# ==========================================

def test_combinacao_de_filtros_e_ordenacao(client):
    client.post(
        "/tarefas",
        json={"titulo": "Z - Python", "tags": ["python"]},
    )

    tarefa = client.post(
        "/tarefas",
        json={"titulo": "A - Python", "tags": ["python"]},
    ).json()

    client.put(
        f"/tarefas/{tarefa['id']}",
        json={
            "titulo": "A - Python",
            "descricao": "",
            "concluida": True,
            "tags": ["python"],
        },
    )

    client.post(
        "/tarefas",
        json={"titulo": "Estudar JavaScript", "tags": ["javascript"]},
    )

    response = client.get(
        "/tarefas?concluida=false&tag=python"
        "&ordenar_por=titulo&ordem=asc"
    )

    assert response.status_code == 200

    dados = response.json()

    assert dados["total"] == 1
    assert dados["tarefas"][0]["titulo"] == "Z - Python"


def test_filtros_combinados_com_data_criacao_decrescente(client):
    primeira = client.post(
        "/tarefas",
        json={"titulo": "Python antigo", "tags": ["python"]},
    ).json()

    time.sleep(0.01)

    segunda = client.post(
        "/tarefas",
        json={"titulo": "Python recente", "tags": ["python"]},
    ).json()

    client.post(
        "/tarefas",
        json={"titulo": "JavaScript", "tags": ["javascript"]},
    )

    response = client.get(
        "/tarefas?concluida=false&tag=python"
        "&ordenar_por=data_criacao&ordem=desc"
    )

    assert response.status_code == 200

    dados = response.json()

    assert dados["total"] == 2
    assert [
        tarefa["id"] for tarefa in dados["tarefas"]
    ] == [segunda["id"], primeira["id"]]


# ==========================================
# 8. TESTES DE VALIDAÇÃO
# ==========================================

def test_rejeitar_tipo_invalido_concluida(client):
    response = client.get("/tarefas?concluida=abc")

    assert response.status_code == 422


@pytest.mark.parametrize(
    "parametro",
    [
        "ordenar_por=invalido",
        "ordem=invalida",
    ],
)
def test_rejeitar_parametros_de_ordenacao_invalidos(
    client, parametro
):
    response = client.get(f"/tarefas?{parametro}")

    assert response.status_code == 422
