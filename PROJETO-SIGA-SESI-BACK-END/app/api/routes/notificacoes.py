from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, validate_current_user_id
from app.database.connection import get_db
from app.services.notificacao_service import NotificacaoService


router = APIRouter()


@router.get("/notificacoes/configuracoes")
def configuracoes_notificacao(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return NotificacaoService(db).get_configurations()


@router.get("/notificacoes/gerenciar")
def listar_notificacoes_criadas(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return NotificacaoService(db).list_created(limit)


@router.post("/notificacoes", status_code=201)
def criar_notificacao(
    titulo: str = Form(...),
    descricao: str = Form(...),
    categoria: str = Form("AVISO"),
    prioridade: str = Form("NORMAL"),
    id_materia: int | None = Form(None),
    id_professor: int | None = Form(None),
    classes: str = Form("[]"),
    alunos: str = Form("[]"),
    solicitar_confirmacao_leitura: bool = Form(False),
    agendada: bool = Form(False),
    data_agendamento: str | None = Form(None),
    publicada: bool = Form(True),
    data_limite: str | None = Form(None),
    permitir_atraso: bool = Form(False),
    ativa: bool = Form(True),
    arquivos: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return NotificacaoService(db).create_notification(
        titulo=titulo,
        descricao=descricao,
        categoria=categoria,
        prioridade=prioridade,
        id_materia=id_materia,
        id_professor=id_professor,
        classes=classes,
        alunos=alunos,
        solicitar_confirmacao_leitura=solicitar_confirmacao_leitura,
        agendada=agendada,
        data_agendamento=data_agendamento,
        publicada=publicada,
        data_limite=data_limite,
        permitir_atraso=permitir_atraso,
        ativa=ativa,
        arquivos=arquivos,
    )


@router.get("/notificacoes/{id_user}")
def listar_notificacoes(
    id_user: int,
    status: str = None,
    materia: str = None,
    categoria: str = None,
    prioridade: str = None,
    dateFrom: str = None,
    dateTo: str = None,
    limit: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    validate_current_user_id(id_user, current_user)
    return NotificacaoService(db).list_student_notifications(
        id_user,
        {
            "status": status,
            "materia": materia,
            "categoria": categoria,
            "prioridade": prioridade,
            "dateFrom": dateFrom,
            "dateTo": dateTo,
            "limit": limit,
        },
    )


@router.put("/notificacoes/{id_mensagem}/{id_user}/confirmar-leitura")
def confirmar_leitura(
    id_mensagem: int,
    id_user: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    validate_current_user_id(id_user, current_user)
    return NotificacaoService(db).confirm_read(id_mensagem, id_user)


@router.put("/notificacoes/todas/{id_user}")
def marcar_todas_lidas(
    id_user: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    validate_current_user_id(id_user, current_user)
    return NotificacaoService(db).mark_all_read(id_user)


@router.get("/dashboard/{id_user}")
def dashboard_aluno(
    id_user: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    validate_current_user_id(id_user, current_user)
    return NotificacaoService(db).get_dashboard(id_user)


@router.get("/usuario/{id_user}")
def get_usuario(
    id_user: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    validate_current_user_id(id_user, current_user)
    return NotificacaoService(db).get_user_summary(id_user)


@router.post("/entrega/{id_mensagem}/{id_aluno}")
def enviar_entrega(
    id_mensagem: int,
    id_aluno: int,
    observacao: str = Form(None),
    arquivos: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    validate_current_user_id(id_aluno, current_user)
    return NotificacaoService(db).send_delivery(
        id_mensagem,
        id_aluno,
        observacao,
        arquivos,
    )
