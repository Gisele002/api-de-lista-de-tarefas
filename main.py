from datetime import date, datetime
from typing import Annotated
from fastapi import FastAPI, HTTPException, Path, Query, Response, status

from schemas import (
    CampoOrdenacao,
    Tarefa,
    TarefaAtualizar,
    TarefaCriar,
    TarefasPaginadas,
    TipoOrdem,
)

# Inicialização da aplicação FastAPI com metadados para o /docs
app = FastAPI(
    title="API de Lista de Tarefas (To-Do)",
    description="Atividade prática da disciplina Programação para Internet II. "
    "Demonstração de CRUD, paginação, filtros, ordenação e validação de dados.",
    version="1.0.0",
)

# Armazenamento em memória (lista Python)
tarefas: list[Tarefa] = []
proximo_id: int = 1


@app.get("/", tags=["Geral"], summary="Informações gerais da API")
def raiz():
    """Retorna mensagem de boas-vindas e indicação da rota de documentação interativa."""
    return {
        "mensagem": "API de Lista de Tarefas - Programação para Internet II",
        "documentacao": "/docs",
    }


# ==========================================
# 1. CRIAR TAREFA (POST /tarefas)
# ==========================================
@app.post(
    "/tarefas",
    response_model=Tarefa,
    status_code=status.HTTP_201_CREATED,
    tags=["Tarefas"],
    summary="Criar uma nova tarefa",
)
def criar_tarefa(dados: TarefaCriar):
    """
    Cria uma nova tarefa e armazena na lista em memória:
    - O **id** é gerado automaticamente.
    - O campo **concluida** inicia como `false`.
    - As datas **data_criacao** e **data_atualizacao** são preenchidas com a data/hora atual.
    """
    global proximo_id

    agora = datetime.now()
    nova_tarefa = Tarefa(
        id=proximo_id,
        titulo=dados.titulo,
        descricao=dados.descricao,
        concluida=False,
        tags=dados.tags,
        data_criacao=agora,
        data_atualizacao=agora,
    )
    tarefas.append(nova_tarefa)
    proximo_id += 1

    return nova_tarefa


# ==========================================
# 2. LISTAR TAREFAS (GET /tarefas)
# ==========================================
@app.get(
    "/tarefas",
    response_model=TarefasPaginadas,
    status_code=status.HTTP_200_OK,
    tags=["Tarefas"],
    summary="Listar tarefas com filtros, ordenação e paginação",
)
def listar_tarefas(
    concluida: Annotated[
        bool | None,
        Query(
            description="Filtrar por situação (true para concluídas, false para pendentes)"
        ),
    ] = None,
    tag: Annotated[
        str | None,
        Query(
            description="Filtrar por tag (busca case-insensitive)"
        ),
    ] = None,
    titulo: Annotated[
        str | None,
        Query(
            description="Filtrar por trecho do título (busca parcial e case-insensitive)"
        ),
    ] = None,
    data_inicio: Annotated[
        date | None,
        Query(
            description="Filtrar tarefas criadas a partir desta data (formato AAAA-MM-DD)"
        ),
    ] = None,
    data_fim: Annotated[
        date | None,
        Query(
            description="Filtrar tarefas criadas até esta data (formato AAAA-MM-DD)"
        ),
    ] = None,
    ordenar_por: Annotated[
        CampoOrdenacao | None,
        Query(
            description="Campo para ordenação (id, titulo, data_criacao, data_atualizacao)"
        ),
    ] = None,
    ordem: Annotated[
        TipoOrdem,
        Query(
            description="Direção da ordenação (asc para crescente, desc para decrescente)"
        ),
    ] = "asc",
    pagina: Annotated[
        int,
        Query(
            ge=1,
            description="Número da página (inicia em 1)"
        ),
    ] = 1,
    limite: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Quantidade máxima de tarefas por página (1 a 100)"
        ),
    ] = 10,
):
    """
    Retorna a lista de tarefas aplicando filtros combinados, ordenação e paginação:
    - **Filtros**: situação (concluida), tag, título e intervalo de datas de criação.
    - **Ordenação**: por id, titulo, data_criacao ou data_atualizacao (asc/desc).
    - **Paginação**: página e limite por página com total de registros pós-filtros.
    """
    # Validação do período de datas
    if data_inicio and data_fim and data_fim < data_inicio:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A data_fim não pode ser anterior à data_inicio.",
        )

    # 1. Aplicação de filtros
    resultado = list(tarefas)

    if concluida is not None:
        resultado = [t for t in resultado if t.concluida == concluida]

    if tag is not None:
        tag_busca = tag.strip().lower()
        resultado = [
            t
            for t in resultado
            if any(tag_busca == t_tag.strip().lower() for t_tag in t.tags)
        ]

    if titulo is not None:
        titulo_busca = titulo.strip().lower()
        resultado = [t for t in resultado if titulo_busca in t.titulo.lower()]

    if data_inicio is not None:
        resultado = [t for t in resultado if t.data_criacao.date() >= data_inicio]

    if data_fim is not None:
        resultado = [t for t in resultado if t.data_criacao.date() <= data_fim]

    # Total de registros correspondentes aos filtros (antes de paginar)
    total = len(resultado)

    # 2. Aplicação de ordenação
    if ordenar_por is not None:
        reverso = ordem == "desc"
        resultado.sort(key=lambda t: getattr(t, ordenar_por), reverse=reverso)

    # 3. Aplicação da paginação
    inicio = (pagina - 1) * limite
    fim = inicio + limite
    tarefas_pagina = resultado[inicio:fim]

    return TarefasPaginadas(
        pagina=pagina,
        limite=limite,
        total=total,
        tarefas=tarefas_pagina,
    )


# ==========================================
# 3. BUSCAR UMA TAREFA POR ID (GET /tarefas/{id})
# ==========================================
@app.get(
    "/tarefas/{id}",
    response_model=Tarefa,
    status_code=status.HTTP_200_OK,
    tags=["Tarefas"],
    summary="Buscar uma tarefa por ID",
)
def buscar_tarefa(
    id: Annotated[
        int,
        Path(ge=1, description="Identificador único da tarefa (número inteiro >= 1)"),
    ],
):
    """
    Busca e retorna uma tarefa específica pelo seu ID.
    - Se a tarefa existir, retorna HTTP 200 com os dados da tarefa.
    - Se não existir, retorna HTTP 404 com mensagem descritiva.
    """
    for tarefa in tarefas:
        if tarefa.id == id:
            return tarefa

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Tarefa com ID {id} não encontrada.",
    )


# ==========================================
# 4. ATUALIZAR TAREFA (PUT /tarefas/{id})
# ==========================================
@app.put(
    "/tarefas/{id}",
    response_model=Tarefa,
    status_code=status.HTTP_200_OK,
    tags=["Tarefas"],
    summary="Atualizar uma tarefa por ID",
)
def atualizar_tarefa(
    id: Annotated[
        int,
        Path(ge=1, description="Identificador único da tarefa (número inteiro >= 1)"),
    ],
    dados: TarefaAtualizar,
):
    """
    Atualiza todos os dados de uma tarefa existente:
    - O **id** e a **data_criacao** original são preservados.
    - A **data_atualizacao** é renovada com a data e hora do momento da edição.
    - Retorna HTTP 404 se a tarefa com o ID fornecido não existir.
    """
    for i, tarefa in enumerate(tarefas):
        if tarefa.id == id:
            tarefa_atualizada = Tarefa(
                id=tarefa.id,
                titulo=dados.titulo,
                descricao=dados.descricao,
                concluida=dados.concluida,
                tags=dados.tags,
                data_criacao=tarefa.data_criacao,
                data_atualizacao=datetime.now(),
            )
            tarefas[i] = tarefa_atualizada
            return tarefa_atualizada

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Tarefa com ID {id} não encontrada.",
    )


# ==========================================
# 5. EXCLUIR TAREFA (DELETE /tarefas/{id})
# ==========================================
@app.delete(
    "/tarefas/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tarefas"],
    summary="Excluir uma tarefa por ID",
)
def excluir_tarefa(
    id: Annotated[
        int,
        Path(ge=1, description="Identificador único da tarefa (número inteiro >= 1)"),
    ],
):
    """
    Remove uma tarefa da lista em memória:
    - Se a tarefa existir, remove e retorna HTTP 204 No Content.
    - Se não existir, retorna HTTP 404 com mensagem descritiva.
    """
    for i, tarefa in enumerate(tarefas):
        if tarefa.id == id:
            tarefas.pop(i)
            return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Tarefa com ID {id} não encontrada.",
    )
