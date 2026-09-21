from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

CampoOrdenacao = Literal["id", "titulo", "data_criacao", "data_atualizacao"]
TipoOrdem = Literal["asc", "desc"]


class TarefaBase(BaseModel):
    """Modelo base com os campos comuns de uma tarefa."""
    titulo: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Título da tarefa (obrigatório)",
        examples=["Estudar FastAPI"]
    )
    descricao: str = Field(
        default="",
        max_length=500,
        description="Descrição detalhada da tarefa",
        examples=["Revisar criação de APIs REST"]
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Lista de tags associadas",
        examples=[["python", "fastapi", "backend"]]
    )


class TarefaCriar(TarefaBase):
    """Schema para os dados recebidos na criação de uma tarefa (POST /tarefas)."""
    pass


class TarefaAtualizar(TarefaBase):
    """Schema para os dados recebidos na atualização de uma tarefa (PUT /tarefas/{id})."""
    concluida: bool = Field(
        ...,
        description="Situação de conclusão da tarefa (true para concluída, false para pendente)",
        examples=[True]
    )


class Tarefa(TarefaBase):
    """Schema representando a tarefa completa com identificador e datas."""
    id: int = Field(
        ...,
        ge=1,
        description="Identificador único da tarefa",
        examples=[1]
    )
    concluida: bool = Field(
        default=False,
        description="Status de conclusão da tarefa",
        examples=[False]
    )
    data_criacao: datetime = Field(
        ...,
        description="Data e hora em que a tarefa foi criada",
        examples=["2026-09-09T08:30:00"]
    )
    data_atualizacao: datetime = Field(
        ...,
        description="Data e hora da última alteração da tarefa",
        examples=["2026-09-09T08:30:00"]
    )


class TarefasPaginadas(BaseModel):
    """Schema de resposta paginada para a listagem de tarefas."""
    pagina: int = Field(..., ge=1, description="Número da página atual", examples=[1])
    limite: int = Field(..., ge=1, description="Quantidade máxima de itens por página", examples=[10])
    total: int = Field(..., ge=0, description="Total de tarefas encontradas após os filtros", examples=[1])
    tarefas: list[Tarefa] = Field(default_factory=list, description="Lista de tarefas da página atual")
