import json
import httpx

BASE_URL = "http://127.0.0.1:8000"


def imprimir_passo(titulo: str):
    print("\n" + "=" * 60)
    print(f"[*] {titulo}")
    print("=" * 60)


def formatar_json(dados):
    return json.dumps(dados, indent=2, ensure_ascii=False)


def main():
    print("\n>>> INICIANDO TESTES PRATICOS NA API...")

    with httpx.Client(base_url=BASE_URL) as client:
        # 1. Teste da rota raiz
        imprimir_passo("1. GET / (Verificando se a API esta online)")
        resp = client.get("/")
        print(f"Status: {resp.status_code}")
        print("Resposta:", formatar_json(resp.json()))

        # 2. Criar primeira tarefa
        imprimir_passo("2. POST /tarefas (Criando Tarefa 1 - Estudar Python)")
        tarefa1 = {
            "titulo": "Estudar Python",
            "descricao": "Revisar listas, dicionarios e funcoes",
            "tags": ["python", "backend"],
        }
        resp = client.post("/tarefas", json=tarefa1)
        print(f"Status: {resp.status_code} (Esperado: 201 Created)")
        print("Tarefa Criada:", formatar_json(resp.json()))

        # 3. Criar segunda tarefa
        imprimir_passo("3. POST /tarefas (Criando Tarefa 2 - Aprender FastAPI)")
        tarefa2 = {
            "titulo": "Aprender FastAPI",
            "descricao": "Estudar rotas, schemas Pydantic e parametros",
            "tags": ["python", "fastapi", "web"],
        }
        resp = client.post("/tarefas", json=tarefa2)
        print(f"Status: {resp.status_code} (Esperado: 201 Created)")
        print("Tarefa Criada:", formatar_json(resp.json()))

        # 4. Criar terceira tarefa
        imprimir_passo("4. POST /tarefas (Criando Tarefa 3 - Estudar Frontend HTML/CSS)")
        tarefa3 = {
            "titulo": "Estudar Frontend HTML/CSS",
            "descricao": "Criar paginas simples com HTML e CSS",
            "tags": ["frontend", "html"],
        }
        resp = client.post("/tarefas", json=tarefa3)
        print(f"Status: {resp.status_code} (Esperado: 201 Created)")
        print("Tarefa Criada:", formatar_json(resp.json()))

        # 5. Listar todas as tarefas
        imprimir_passo("5. GET /tarefas (Listando todas as tarefas)")
        resp = client.get("/tarefas")
        print(f"Status: {resp.status_code}")
        print("Resposta Paginada:", formatar_json(resp.json()))

        # 6. Buscar tarefa por ID
        imprimir_passo("6. GET /tarefas/1 (Buscando tarefa pelo ID 1)")
        resp = client.get("/tarefas/1")
        print(f"Status: {resp.status_code}")
        print("Tarefa Encontrada:", formatar_json(resp.json()))

        # 7. Atualizar tarefa
        imprimir_passo("7. PUT /tarefas/1 (Concluindo a Tarefa 1)")
        atualizacao = {
            "titulo": "Estudar Python Avancado",
            "descricao": "Revisar listas, dicionarios e funcoes avancadas",
            "concluida": True,
            "tags": ["python", "backend", "concluido"],
        }
        resp = client.put("/tarefas/1", json=atualizacao)
        print(f"Status: {resp.status_code}")
        print("Tarefa Atualizada:", formatar_json(resp.json()))

        # 8. Filtro por Situacao (apenas concluidas)
        imprimir_passo("8. GET /tarefas?concluida=true (Filtrando tarefas concluidas)")
        resp = client.get("/tarefas?concluida=true")
        print(f"Total encontradas: {resp.json()['total']}")
        print("Tarefas:", formatar_json(resp.json()["tarefas"]))

        # 9. Filtro por Tag
        imprimir_passo("9. GET /tarefas?tag=fastapi (Filtrando por tag 'fastapi')")
        resp = client.get("/tarefas?tag=fastapi")
        print(f"Total encontradas: {resp.json()['total']}")
        print("Tarefas:", formatar_json(resp.json()["tarefas"]))

        # 10. Filtro por Titulo (busca parcial)
        imprimir_passo("10. GET /tarefas?titulo=Python (Buscando tarefas com 'Python' no titulo)")
        resp = client.get("/tarefas?titulo=Python")
        print(f"Total encontradas: {resp.json()['total']}")
        print("Tarefas:", formatar_json(resp.json()["tarefas"]))

        # 11. Ordenacao
        imprimir_passo("11. GET /tarefas?ordenar_por=titulo&ordem=asc (Ordenando por titulo A-Z)")
        resp = client.get("/tarefas?ordenar_por=titulo&ordem=asc")
        titulos = [t["titulo"] for t in resp.json()["tarefas"]]
        print("Ordem dos Titulos:", titulos)

        # 12. Teste de ID inexistente (404)
        imprimir_passo("12. GET /tarefas/999 (Testando busca de ID inexistente)")
        resp = client.get("/tarefas/999")
        print(f"Status: {resp.status_code} (Esperado: 404 Not Found)")
        print("Resposta:", formatar_json(resp.json()))

        # 13. Excluir uma tarefa
        imprimir_passo("13. DELETE /tarefas/3 (Excluindo a Tarefa 3)")
        resp = client.delete("/tarefas/3")
        print(f"Status: {resp.status_code} (Esperado: 204 No Content)")

        # 14. Conferir listagem final
        imprimir_passo("14. GET /tarefas (Conferindo lista apos exclusao)")
        resp = client.get("/tarefas")
        print(f"Total restante: {resp.json()['total']}")
        print("Tarefas restantes:", formatar_json(resp.json()["tarefas"]))

    print("\n" + "=" * 60)
    print("[SUCESSO] TODOS OS TESTES FORAM CONCLUIDOS COM SUCESSO!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
