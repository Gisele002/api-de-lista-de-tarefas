# API de Lista de Tarefas (To-Do)

Atividade prática desenvolvida para a disciplina **Programação para Internet II**, utilizando **Python** e **FastAPI**.

---

## 🎯 Objetivo

Desenvolver uma API REST simples, clara e robusta para gerenciamento de tarefas (CRUD), aplicando conceitos fundamentais da disciplina:
- Métodos e Status HTTP (200, 201, 204, 404, 422);
- Arquitetura REST e formato JSON;
- Path Parameters e Query Parameters com validação e metadados;
- Modelos de dados, serialização e validação com **Pydantic** (`BaseModel`, `Field`, `Annotated`);
- Armazenamento de dados em memória (lista Python);
- Recursos de filtragem (situação, tags, busca por título), ordenação, paginação e consulta por período;
- Documentação interativa automática com Swagger UI (`/docs`) e ReDoc (`/redoc`).

---

## 🛠️ Tecnologias Utilizadas

- **Python** (versão 3.10+)
- **FastAPI** (framework web assíncrono de alta performance)
- **Pydantic** (validação e tipagem de dados)
- **uv** (gerenciador rápido de projetos e pacotes Python)
- **HTTP / JSON** (comunicação e serialização de dados)
- **Pytest / HTTPX** (testes automatizados da API)

---

## 📁 Estrutura do Projeto

```text
api_de_tarefas/
├── main.py          # Aplicação FastAPI, endpoints e regras de negócio
├── schemas.py       # Modelos de dados e validações com Pydantic
├── test_main.py     # Suíte de testes automatizados com Pytest
├── pyproject.toml   # Configuração do projeto e dependências
├── uv.lock          # Arquivo de lock de dependências
└── README.md        # Documentação do projeto
```

---

## 🚀 Como Instalar e Executar

### 1. Pré-requisitos
Certifique-se de ter o `uv` instalado. Se ainda não possuir:
```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clonar / Entrar no diretório do projeto
```bash
cd api_de_tarefas
```

### 3. Instalar dependências
```bash
uv sync
```

### 4. Executar a API em modo desenvolvimento
```bash
uv run fastapi dev main.py
```

A API estará acessível em:
- **URL Base:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Documentação Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Documentação ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 5. Executar os Testes Automatizados
```bash
uv run pytest
```

---

## 📋 Endpoints da API

| Método | Endpoint | Descrição | Status de Sucesso |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Informações gerais e link para documentação | `200 OK` |
| `POST` | `/tarefas` | Cadastra uma nova tarefa | `201 Created` |
| `GET` | `/tarefas` | Lista tarefas com paginação, filtros e ordenação | `200 OK` |
| `GET` | `/tarefas/{id}` | Busca uma tarefa específica pelo ID | `200 OK` |
| `PUT` | `/tarefas/{id}` | Atualiza uma tarefa existente | `200 OK` |
| `DELETE` | `/tarefas/{id}` | Remove uma tarefa existente | `204 No Content` |

---

## 📝 Exemplos de Requisições

### 1. Criar Tarefa (`POST /tarefas`)
**Corpo da Requisição (JSON):**
```json
{
  "titulo": "Estudar FastAPI",
  "descricao": "Revisar criação de rotas, validações e schemas",
  "tags": ["python", "fastapi", "backend"]
}
```

**Resposta (`201 Created`):**
```json
{
  "id": 1,
  "titulo": "Estudar FastAPI",
  "descricao": "Revisar criação de rotas, validações e schemas",
  "concluida": false,
  "tags": ["python", "fastapi", "backend"],
  "data_criacao": "2026-09-21T14:55:00.123456",
  "data_atualizacao": "2026-09-21T14:55:00.123456"
}
```

---

### 2. Buscar Tarefa por ID (`GET /tarefas/1`)
**Resposta (`200 OK`):**
```json
{
  "id": 1,
  "titulo": "Estudar FastAPI",
  "descricao": "Revisar criação de rotas, validações e schemas",
  "concluida": false,
  "tags": ["python", "fastapi", "backend"],
  "data_criacao": "2026-09-21T14:55:00.123456",
  "data_atualizacao": "2026-09-21T14:55:00.123456"
}
```

*Caso o ID não exista:* Retorna `404 Not Found` com `{"detail": "Tarefa com ID 99 não encontrada."}`.

---

### 3. Atualizar Tarefa (`PUT /tarefas/1`)
**Corpo da Requisição (JSON):**
```json
{
  "titulo": "Estudar FastAPI Avançado",
  "descricao": "Estudar rotas, parâmetros e respostas",
  "concluida": true,
  "tags": ["python", "fastapi"]
}
```

**Resposta (`200 OK`):**
```json
{
  "id": 1,
  "titulo": "Estudar FastAPI Avançado",
  "descricao": "Estudar rotas, parâmetros e respostas",
  "concluida": true,
  "tags": ["python", "fastapi"],
  "data_criacao": "2026-09-21T14:55:00.123456",
  "data_atualizacao": "2026-09-21T15:10:25.654321"
}
```
*(Observe que a `data_criacao` é mantida e a `data_atualizacao` é renovada automaticamente).*

---

### 4. Excluir Tarefa (`DELETE /tarefas/1`)
**Resposta (`204 No Content`):** Corpo vazio.

---

## 🔍 Exemplos de Query Parameters (`GET /tarefas`)

O endpoint `GET /tarefas` suporta filtros combinados, paginação e ordenação:

### Estrutura da Resposta Paginada
```json
{
  "pagina": 1,
  "limite": 10,
  "total": 1,
  "tarefas": [
    {
      "id": 1,
      "titulo": "Estudar FastAPI",
      "descricao": "Revisar criação de APIs REST",
      "concluida": false,
      "tags": ["python", "fastapi", "backend"],
      "data_criacao": "2026-09-21T14:55:00.123456",
      "data_atualizacao": "2026-09-21T14:55:00.123456"
    }
  ]
}
```

### 1. Filtro por Situação
- Apenas pendentes: `GET /tarefas?concluida=false`
- Apenas concluídas: `GET /tarefas?concluida=true`

### 2. Filtro por Tag (case-insensitive)
- `GET /tarefas?tag=python`

### 3. Filtro por Título (busca parcial)
- `GET /tarefas?titulo=fastapi`

### 4. Consulta por Período de Criação
- Intervalo de datas: `GET /tarefas?data_inicio=2026-09-01&data_fim=2026-09-30`
- Apenas a partir de uma data: `GET /tarefas?data_inicio=2026-09-15`
- Apenas até uma data: `GET /tarefas?data_fim=2026-09-20`

### 5. Ordenação
- Por título ascendente: `GET /tarefas?ordenar_por=titulo&ordem=asc`
- Por data de criação decrescente: `GET /tarefas?ordenar_por=data_criacao&ordem=desc`
- Campos disponíveis para ordenação: `id`, `titulo`, `data_criacao`, `data_atualizacao`.

### 6. Paginação
- Segunda página com 5 tarefas por página: `GET /tarefas?pagina=2&limite=5`

### 7. Combinação de Múltiplos Filtros
- Tarefas não concluídas com a tag "python", ordenadas pelas mais recentes:
  `GET /tarefas?concluida=false&tag=python&ordenar_por=data_criacao&ordem=desc`
