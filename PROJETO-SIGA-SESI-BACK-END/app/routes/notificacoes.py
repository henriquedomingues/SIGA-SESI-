from fastapi import UploadFile, File, Form, HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db


import base64
import json
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

#chat gpt fes - inicio dos recursos para criar e gerenciar notificacoes
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024


def _parse_id_list(raw_value: str | None, field_name: str) -> list[int]:
    if not raw_value:
        return []

    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} deve ser uma lista JSON valida"
        ) from exc

    if not isinstance(value, list):
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} deve ser uma lista"
        )

    try:
        return list(dict.fromkeys(int(item) for item in value))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} contem um identificador invalido"
        ) from exc


def _parse_datetime(raw_value: str | None, field_name: str) -> datetime | None:
    if not raw_value:
        return None

    try:
        return datetime.fromisoformat(raw_value.replace("Z", "+00:00")).replace(
            tzinfo=None
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} deve conter uma data e hora valida"
        ) from exc


def _validate_existing_ids(
    db: Session,
    table: str,
    column: str,
    ids: list[int],
    field_name: str
) -> None:
    if not ids:
        return

    placeholders = ", ".join(f":id_{index}" for index in range(len(ids)))
    params = {f"id_{index}": value for index, value in enumerate(ids)}
    rows = db.execute(
        text(f"SELECT {column} FROM {table} WHERE {column} IN ({placeholders})"),
        params
    ).fetchall()
    existing_ids = {int(row[0]) for row in rows}
    missing_ids = sorted(set(ids) - existing_ids)

    if missing_ids:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} inexistente(s): {missing_ids}"
        )


# =====================================================
# CONFIGURACOES PARA CRIAR NOTIFICACOES
# =====================================================
@router.get("/notificacoes/configuracoes")
def configuracoes_notificacao(db: Session = Depends(get_db)):
    classes = db.execute(text("""
        SELECT
            c.idClasseDeAula AS id,
            c.nomeClasse AS nome,
            c.anoLetivo,
            c.idEscola,
            COUNT(a.idUser) AS totalAlunos
        FROM tblClasseDeAula c
        LEFT JOIN tblAluno a
            ON a.idClasseDeAula = c.idClasseDeAula
        GROUP BY
            c.idClasseDeAula,
            c.nomeClasse,
            c.anoLetivo,
            c.idEscola
        ORDER BY c.anoLetivo DESC, c.nomeClasse
    """)).mappings().all()

    materias = db.execute(text("""
        SELECT idMateria AS id, nomeMateria AS nome
        FROM tblMateria
        ORDER BY nomeMateria
    """)).mappings().all()

    alunos = db.execute(text("""
        SELECT
            a.idUser AS id,
            u.nomeUser AS nome,
            a.idClasseDeAula,
            c.nomeClasse AS turma
        FROM tblAluno a
        JOIN tblUser u
            ON u.idUser = a.idUser
        LEFT JOIN tblClasseDeAula c
            ON c.idClasseDeAula = a.idClasseDeAula
        ORDER BY u.nomeUser
    """)).mappings().all()

    professores = db.execute(text("""
        SELECT p.idUser AS id, u.nomeUser AS nome
        FROM tblProfessor p
        JOIN tblUser u
            ON u.idUser = p.idUser
        ORDER BY u.nomeUser
    """)).mappings().all()

    return {
        "categorias": ["AVISO", "ATIVIDADE"],
        "prioridades": ["BAIXA", "NORMAL", "ALTA", "URGENTE"],
        "classes": [dict(row) for row in classes],
        "materias": [dict(row) for row in materias],
        "alunos": [dict(row) for row in alunos],
        "professores": [dict(row) for row in professores]
    }


# =====================================================
# LISTAR NOTIFICACOES CRIADAS
# =====================================================
@router.get("/notificacoes/gerenciar")
def listar_notificacoes_criadas(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    safe_limit = max(1, min(limit, 100))
    rows = db.execute(text("""
        SELECT
            m.idMensagem AS id,
            m.tituloMensagem AS titulo,
            m.descricaoMensagem AS descricao,
            m.dataMensagem,
            m.idMateria,
            mat.nomeMateria AS materia,
            m.idClasseDeAula,
            c.nomeClasse AS turmaPrincipal,
            m.idProfessor,
            u.nomeUser AS professor,
            m.categoria,
            m.prioridade,
            m.solicitarConfirmacaoLeitura,
            m.agendada,
            m.dataAgendamento,
            m.publicada,
            m.dataLimite,
            m.permitirAtraso,
            m.ativa,
            COUNT(DISTINCT ma.idUser) AS totalDestinatarios,
            COUNT(DISTINCT mc.idClasseDeAula) AS totalTurmas,
            COUNT(DISTINCT an.idAnexo) AS totalAnexos
        FROM tblMensagem m
        LEFT JOIN tblMateria mat
            ON mat.idMateria = m.idMateria
        LEFT JOIN tblClasseDeAula c
            ON c.idClasseDeAula = m.idClasseDeAula
        LEFT JOIN tblProfessor p
            ON p.idUser = m.idProfessor
        LEFT JOIN tblUser u
            ON u.idUser = p.idUser
        LEFT JOIN tblMensagemAluno ma
            ON ma.idMensagem = m.idMensagem
        LEFT JOIN tblMensagemClasse mc
            ON mc.idMensagem = m.idMensagem
        LEFT JOIN tblAnexo an
            ON an.idMensagem = m.idMensagem
        GROUP BY
            m.idMensagem,
            m.tituloMensagem,
            m.descricaoMensagem,
            m.dataMensagem,
            m.idMateria,
            mat.nomeMateria,
            m.idClasseDeAula,
            c.nomeClasse,
            m.idProfessor,
            u.nomeUser,
            m.categoria,
            m.prioridade,
            m.solicitarConfirmacaoLeitura,
            m.agendada,
            m.dataAgendamento,
            m.publicada,
            m.dataLimite,
            m.permitirAtraso,
            m.ativa
        ORDER BY m.idMensagem DESC
        LIMIT :limit
    """), {"limit": safe_limit}).mappings().all()

    return [dict(row) for row in rows]


# =====================================================
# CRIAR NOTIFICACAO
# =====================================================
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
    db: Session = Depends(get_db)
):
    titulo = titulo.strip()
    descricao = descricao.strip()
    categoria = categoria.upper()
    prioridade = prioridade.upper()
    class_ids = _parse_id_list(classes, "classes")
    direct_student_ids = _parse_id_list(alunos, "alunos")
    scheduled_at = _parse_datetime(data_agendamento, "data_agendamento")
    deadline = _parse_datetime(data_limite, "data_limite")

    if not titulo or len(titulo) > 150:
        raise HTTPException(
            status_code=422,
            detail="O titulo deve ter entre 1 e 150 caracteres"
        )
    if not descricao or len(descricao) > 600:
        raise HTTPException(
            status_code=422,
            detail="A descricao deve ter entre 1 e 600 caracteres"
        )
    if categoria not in {"AVISO", "ATIVIDADE"}:
        raise HTTPException(status_code=422, detail="Categoria invalida")
    if prioridade not in {"BAIXA", "NORMAL", "ALTA", "URGENTE"}:
        raise HTTPException(status_code=422, detail="Prioridade invalida")
    if not class_ids and not direct_student_ids:
        raise HTTPException(
            status_code=422,
            detail="Selecione ao menos uma turma ou um aluno"
        )
    if agendada and not scheduled_at:
        raise HTTPException(
            status_code=422,
            detail="Informe a data de agendamento"
        )
    if agendada and scheduled_at and scheduled_at <= datetime.now():
        raise HTTPException(
            status_code=422,
            detail="A data de agendamento deve estar no futuro"
        )
    if categoria == "ATIVIDADE" and not deadline:
        raise HTTPException(
            status_code=422,
            detail="Atividades precisam de uma data limite"
        )
    if deadline and scheduled_at and deadline <= scheduled_at:
        raise HTTPException(
            status_code=422,
            detail="A data limite deve ser posterior ao agendamento"
        )

    _validate_existing_ids(
        db, "tblClasseDeAula", "idClasseDeAula", class_ids, "Turma"
    )
    _validate_existing_ids(
        db, "tblAluno", "idUser", direct_student_ids, "Aluno"
    )
    if id_materia is not None:
        _validate_existing_ids(
            db, "tblMateria", "idMateria", [id_materia], "Materia"
        )
    if id_professor is not None:
        _validate_existing_ids(
            db, "tblProfessor", "idUser", [id_professor], "Professor"
        )

    try:
        insert_result = db.execute(text("""
            INSERT INTO tblMensagem (
                tituloMensagem,
                descricaoMensagem,
                idMateria,
                idClasseDeAula,
                idProfessor,
                categoria,
                prioridade,
                solicitarConfirmacaoLeitura,
                agendada,
                dataAgendamento,
                publicada,
                dataLimite,
                permitirAtraso,
                ativa
            ) VALUES (
                :titulo,
                :descricao,
                :idMateria,
                :idClasseDeAula,
                :idProfessor,
                :categoria,
                :prioridade,
                :solicitarConfirmacaoLeitura,
                :agendada,
                :dataAgendamento,
                :publicada,
                :dataLimite,
                :permitirAtraso,
                :ativa
            )
        """), {
            "titulo": titulo,
            "descricao": descricao,
            "idMateria": id_materia,
            "idClasseDeAula": class_ids[0] if class_ids else None,
            "idProfessor": id_professor,
            "categoria": categoria,
            "prioridade": prioridade,
            "solicitarConfirmacaoLeitura": solicitar_confirmacao_leitura,
            "agendada": agendada,
            "dataAgendamento": scheduled_at,
            "publicada": publicada and not agendada,
            "dataLimite": deadline if categoria == "ATIVIDADE" else None,
            "permitirAtraso": permitir_atraso if categoria == "ATIVIDADE" else False,
            "ativa": ativa
        })
        message_id = int(insert_result.lastrowid)

        for class_id in class_ids:
            db.execute(text("""
                INSERT INTO tblMensagemClasse (idMensagem, idClasseDeAula)
                VALUES (:idMensagem, :idClasseDeAula)
            """), {
                "idMensagem": message_id,
                "idClasseDeAula": class_id
            })

        class_student_ids: set[int] = set()
        if class_ids:
            placeholders = ", ".join(
                f":class_{index}" for index in range(len(class_ids))
            )
            params = {
                f"class_{index}": value
                for index, value in enumerate(class_ids)
            }
            students = db.execute(text(f"""
                SELECT idUser
                FROM tblAluno
                WHERE idClasseDeAula IN ({placeholders})
            """), params).fetchall()
            class_student_ids = {int(row.idUser) for row in students}

        recipient_ids = class_student_ids | set(direct_student_ids)
        for student_id in recipient_ids:
            db.execute(text("""
                INSERT INTO tblMensagemAluno (
                    idMensagem,
                    idUser,
                    destinatarioDireto
                ) VALUES (
                    :idMensagem,
                    :idUser,
                    :destinatarioDireto
                )
                ON DUPLICATE KEY UPDATE
                    destinatarioDireto = VALUES(destinatarioDireto)
            """), {
                "idMensagem": message_id,
                "idUser": student_id,
                "destinatarioDireto": student_id in direct_student_ids
            })

        saved_attachments = []
        for arquivo in arquivos:
            content = arquivo.file.read()
            if len(content) > MAX_ATTACHMENT_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"O arquivo {arquivo.filename} excede 10 MB"
                )

            attachment_result = db.execute(text("""
                INSERT INTO tblAnexo (
                    idMensagem,
                    nomeArquivo,
                    tipoArquivo,
                    tamanhoArquivo,
                    arquivo
                ) VALUES (
                    :idMensagem,
                    :nomeArquivo,
                    :tipoArquivo,
                    :tamanhoArquivo,
                    :arquivo
                )
            """), {
                "idMensagem": message_id,
                "nomeArquivo": arquivo.filename or "arquivo",
                "tipoArquivo": arquivo.content_type,
                "tamanhoArquivo": len(content),
                "arquivo": content
            })
            saved_attachments.append({
                "id": int(attachment_result.lastrowid),
                "nome": arquivo.filename or "arquivo",
                "tipo": arquivo.content_type,
                "tamanho": len(content)
            })

        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Erro ao criar notificacao")
        raise HTTPException(
            status_code=500,
            detail="Nao foi possivel criar a notificacao"
        ) from exc

    return {
        "success": True,
        "id": message_id,
        "totalDestinatarios": len(recipient_ids),
        "totalTurmas": len(class_ids),
        "anexos": saved_attachments,
        "status": (
            "AGENDADA"
            if agendada
            else "PUBLICADA"
            if publicada
            else "RASCUNHO"
        )
    }
#chat gpt fes - fim dos recursos para criar e gerenciar notificacoes


# =====================================================
# LISTAR MENSAGENS / ATIVIDADES DO ALUNO
# =====================================================
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
    db: Session = Depends(get_db)
):

    query = """
        SELECT

            m.idMensagem,
            m.tituloMensagem,
            m.descricaoMensagem,
            m.dataMensagem,

            m.categoria,
            m.prioridade,

            m.dataLimite,
            m.permitirAtraso,

            ma.lida,
            ma.dataLeitura,

            e.idEntrega,
            e.entregue,
            e.atrasada,
            e.bloqueada,
            e.dataEnvio,
            e.nota,
            e.comentarioProfessor,
            e.corrigida,

            COALESCE(mat.nomeMateria,'Geral') AS nomeMateria

        FROM tblMensagem m

        JOIN tblMensagemAluno ma
            ON ma.idMensagem = m.idMensagem

        LEFT JOIN tblMateria mat
            ON mat.idMateria = m.idMateria

        LEFT JOIN tblEntregaAtividade e
            ON e.idMensagem = m.idMensagem
            AND e.idAluno = ma.idUser

        WHERE ma.idUser = :id_user
          AND m.ativa = TRUE
          AND (
                m.publicada = TRUE
                OR (
                    m.agendada = TRUE
                    AND m.dataAgendamento <= NOW()
                )
          )
    """

    params = {
        "id_user": id_user
    }

    # ==========================
    # FILTRO LEITURA
    # ==========================

    if status == "read":
        query += " AND ma.lida = TRUE"

    elif status == "unread":
        query += " AND ma.lida = FALSE"

    # ==========================
    # FILTRO MATÉRIA
    # ==========================

    if materia and materia != "Todas as matérias":
        query += """
            AND COALESCE(mat.nomeMateria,'Geral') = :materia
        """
        params["materia"] = materia

    # ==========================
    # FILTRO CATEGORIA
    # ==========================

    if categoria:
        query += " AND m.categoria = :categoria"
        params["categoria"] = categoria

    # ==========================
    # FILTRO PRIORIDADE
    # ==========================

    if prioridade:
        query += " AND m.prioridade = :prioridade"
        params["prioridade"] = prioridade

    # ==========================
    # FILTRO DATA
    # ==========================

    if dateFrom:
        query += " AND DATE(m.dataMensagem) >= :dateFrom"
        params["dateFrom"] = dateFrom

    if dateTo:
        query += " AND DATE(m.dataMensagem) <= :dateTo"
        params["dateTo"] = dateTo

    # ==========================
    # ORDENAÇÃO
    # ==========================

    query += """
        ORDER BY
            CASE m.prioridade
                WHEN 'URGENTE' THEN 1
                WHEN 'ALTA' THEN 2
                WHEN 'NORMAL' THEN 3
                WHEN 'BAIXA' THEN 4
            END,
            m.dataMensagem DESC
    """

    # ==========================
    # LIMIT
    # ==========================

    if limit:
        query += " LIMIT :limit"
        params["limit"] = int(limit)

    result = db.execute(
        text(query),
        params
    ).fetchall()

    # ==========================
# CARREGAR ANEXOS
# ==========================

    anexos_map = {}

    ids = [row.idMensagem for row in result]

    if ids:
        placeholders = ",".join(str(i) for i in ids)

        anexos_rows = db.execute(text(f"""
            SELECT
                idAnexo,
                idMensagem,
                nomeArquivo,
                tipoArquivo
            FROM tblanexo
            WHERE idMensagem IN ({placeholders})
        """)).fetchall()

        for a in anexos_rows:
            anexos_map.setdefault(a.idMensagem, []).append({
                "idAnexo": a.idAnexo,
                "nome": a.nomeArquivo,
                "tipo": a.tipoArquivo
            })

    return [

        {
            "id": row.idMensagem,

            "titulo": row.tituloMensagem,

            "descricao": row.descricaoMensagem,

            "data": str(row.dataMensagem)
            if row.dataMensagem else None,

            "categoria": row.categoria,

            "prioridade": row.prioridade,

            "materia": row.nomeMateria,

            "dataLimite": str(row.dataLimite)
            if row.dataLimite else None,

            "permitirAtraso": bool(row.permitirAtraso)
            if row.permitirAtraso is not None else False,

            "lida": bool(row.lida),

            "dataLeitura": str(row.dataLeitura)
            if row.dataLeitura else None,

            "entregue": bool(row.entregue)
            if row.entregue is not None else False,

            "atrasada": bool(row.atrasada)
            if row.atrasada is not None else False,

            "bloqueada": bool(row.bloqueada)
            if row.bloqueada is not None else False,

            "dataEnvio": str(row.dataEnvio)
            if row.dataEnvio else None,

            "nota": float(row.nota)
            if row.nota is not None else None,

            "comentarioProfessor":
                row.comentarioProfessor,

            "corrigida": bool(row.corrigida)
            if row.corrigida is not None else False,

            "anexos": anexos_map.get(row.idMensagem, [])
        }

        for row in result
    ]


# =====================================================
# CONFIRMAR LEITURA
# =====================================================
@router.put(
    "/notificacoes/{id_mensagem}/{id_user}/confirmar-leitura"
)
def confirmar_leitura(
    id_mensagem: int,
    id_user: int,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            UPDATE tblMensagemAluno
            SET
                lida = TRUE,
                dataLeitura = NOW()
            WHERE
                idMensagem = :idMensagem
                AND idUser = :idUser
        """),
        {
            "idMensagem": id_mensagem,
            "idUser": id_user
        }
    )

    db.commit()

    return {
        "success": True
    }


# =====================================================
# MARCAR TODAS COMO LIDAS
# =====================================================
@router.put(
    "/notificacoes/todas/{id_user}"
)
def marcar_todas_lidas(
    id_user: int,
    db: Session = Depends(get_db)
):

    db.execute(
        text("""
            UPDATE tblMensagemAluno
            SET
                lida = TRUE,
                dataLeitura = NOW()
            WHERE idUser = :idUser
        """),
        {
            "idUser": id_user
        }
    )

    db.commit()

    return {
        "success": True
    }


# =====================================================
# RESUMO DASHBOARD ALUNO
# =====================================================
@router.get(
    "/dashboard/{id_user}"
)
def dashboard_aluno(
    id_user: int,
    db: Session = Depends(get_db)
):

    result = db.execute(
        text("""
            SELECT

                COUNT(*) totalMensagens,

                SUM(
                    CASE
                        WHEN ma.lida = FALSE
                        THEN 1
                        ELSE 0
                    END
                ) naoLidas,

                SUM(
                    CASE
                        WHEN e.entregue = TRUE
                        THEN 1
                        ELSE 0
                    END
                ) entregues,

                SUM(
                    CASE
                        WHEN e.atrasada = TRUE
                        THEN 1
                        ELSE 0
                    END
                ) atrasadas

            FROM tblMensagemAluno ma

            LEFT JOIN tblEntregaAtividade e
                ON e.idMensagem = ma.idMensagem
                AND e.idAluno = ma.idUser

            WHERE ma.idUser = :idUser
        """),
        {
            "idUser": id_user
        }
    ).fetchone()

    return {

        "totalMensagens":
            result.totalMensagens or 0,

        "naoLidas":
            result.naoLidas or 0,

        "entregues":
            result.entregues or 0,

        "atrasadas":
            result.atrasadas or 0
    }


# =====================================================
# DADOS DO ALUNO
# =====================================================
@router.get("/usuario/{id_user}")
def get_usuario(
    id_user: int,
    db: Session = Depends(get_db)
):

    result = db.execute(
        text("""
            SELECT

                u.nomeUser,
                c.nomeClasse

            FROM tblUser u

            LEFT JOIN tblAluno a
                ON a.idUser = u.idUser

            LEFT JOIN tblClasseDeAula c
                ON c.idClasseDeAula = a.idClasseDeAula

            WHERE u.idUser = :id_user
        """),
        {
            "id_user": id_user
        }
    ).fetchone()

    if not result:

        return {
            "nome": "Usuário",
            "turma": ""
        }

    return {

        "nome": result.nomeUser,

        "turma":
            result.nomeClasse
            if result.nomeClasse
            else ""
    }

# =====================================================
# ALUNO — ENVIAR ENTREGA COM ARQUIVO
# =====================================================


@router.post("/entrega/{id_mensagem}/{id_aluno}")
def enviar_entrega(

    id_mensagem: int,
    id_aluno: int,
    observacao: str = Form(None),
    arquivos: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):



    row = db.execute(text("""
        SELECT idEntrega, bloqueada FROM tblentregaatividade
        WHERE idMensagem = :idMensagem AND idAluno = :idAluno
    """), {"idMensagem": id_mensagem, "idAluno": id_aluno}).fetchone()


    
    if not row:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
    if row.bloqueada:
        raise HTTPException(status_code=403, detail="Entrega bloqueada")

    # Verifica atraso
    prazo = db.execute(text(
        "SELECT dataLimite, permitirAtraso FROM tblmensagem WHERE idMensagem = :id"
    ), {"id": id_mensagem}).fetchone()

    atrasada = False
    if prazo.dataLimite:
        from datetime import datetime
        atrasada = datetime.now() > prazo.dataLimite
        if atrasada and not prazo.permitirAtraso:
            raise HTTPException(status_code=403, detail="Prazo encerrado")

    db.execute(text("""
        UPDATE tblentregaatividade SET
            entregue = TRUE,
            atrasada = :atrasada,
            observacaoAluno = :obs,
            dataEnvio = NOW()
        WHERE idEntrega = :idEntrega
    """), {"atrasada": atrasada, "obs": observacao, "idEntrega": row.idEntrega})

    for arquivo in arquivos:
        conteudo = arquivo.file.read()
        db.execute(text("""
            INSERT INTO tblarquivoentrega (idEntrega, nomeArquivo, tipoArquivo, tamanhoArquivo, arquivo)
            VALUES (:idEntrega, :nome, :tipo, :tamanho, :arquivo)
        """), {
            "idEntrega": row.idEntrega, "nome": arquivo.filename,
            "tipo": arquivo.content_type, "tamanho": len(conteudo),
            "arquivo": conteudo
        })
    db.commit()
    return {"success": True, "atrasada": atrasada}
