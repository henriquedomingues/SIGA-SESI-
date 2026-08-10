import logging
from datetime import datetime

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.repositories.notificacao_repository import NotificacaoRepository
from app.utils.parsers import parse_datetime, parse_id_list


logger = logging.getLogger(__name__)

MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024
VALIDATION_TARGETS = {
    "Turma": ("tblClasseDeAula", "idClasseDeAula"),
    "Aluno": ("tblAluno", "idUser"),
    "Materia": ("tblMateria", "idMateria"),
    "Professor": ("tblProfessor", "idUser"),
}


class NotificacaoService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = NotificacaoRepository(db)

    def get_configurations(self) -> dict:
        configurations = self.repository.get_configurations()
        return {
            "categorias": ["AVISO", "ATIVIDADE"],
            "prioridades": ["BAIXA", "NORMAL", "ALTA", "URGENTE"],
            **configurations,
        }

    def list_created(self, limit: int = 20) -> list[dict]:
        safe_limit = max(1, min(limit, 100))
        return [dict(row) for row in self.repository.list_created(safe_limit)]

    def create_notification(
        self,
        titulo: str,
        descricao: str,
        categoria: str,
        prioridade: str,
        id_materia: int | None,
        id_professor: int | None,
        classes: str,
        alunos: str,
        solicitar_confirmacao_leitura: bool,
        agendada: bool,
        data_agendamento: str | None,
        publicada: bool,
        data_limite: str | None,
        permitir_atraso: bool,
        ativa: bool,
        arquivos: list[UploadFile],
    ) -> dict:
        titulo = titulo.strip()
        descricao = descricao.strip()
        categoria = categoria.upper()
        prioridade = prioridade.upper()
        class_ids = parse_id_list(classes, "classes")
        direct_student_ids = parse_id_list(alunos, "alunos")
        scheduled_at = parse_datetime(data_agendamento, "data_agendamento")
        deadline = parse_datetime(data_limite, "data_limite")

        self._validate_notification_data(
            titulo=titulo,
            descricao=descricao,
            categoria=categoria,
            prioridade=prioridade,
            class_ids=class_ids,
            direct_student_ids=direct_student_ids,
            agendada=agendada,
            scheduled_at=scheduled_at,
            deadline=deadline,
        )
        self._validate_existing_ids("Turma", class_ids)
        self._validate_existing_ids("Aluno", direct_student_ids)
        if id_materia is not None:
            self._validate_existing_ids("Materia", [id_materia])
        if id_professor is not None:
            self._validate_existing_ids("Professor", [id_professor])

        try:
            message_id = self.repository.create_message({
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
                "ativa": ativa,
            })

            for class_id in class_ids:
                self.repository.add_message_class(message_id, class_id)

            class_student_ids = self.repository.get_student_ids_by_class_ids(class_ids)
            recipient_ids = class_student_ids | set(direct_student_ids)
            for student_id in recipient_ids:
                self.repository.upsert_message_student(
                    message_id,
                    student_id,
                    student_id in direct_student_ids,
                )

            saved_attachments = self._save_message_attachments(message_id, arquivos)
            self.db.commit()
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            logger.exception("Erro ao criar notificacao")
            raise HTTPException(
                status_code=500,
                detail="Nao foi possivel criar a notificacao",
            ) from exc

        return {
            "success": True,
            "id": message_id,
            "totalDestinatarios": len(recipient_ids),
            "totalTurmas": len(class_ids),
            "anexos": saved_attachments,
            "status": "AGENDADA" if agendada else "PUBLICADA" if publicada else "RASCUNHO",
        }

    def list_student_notifications(self, user_id: int, filters: dict) -> list[dict]:
        rows = self.repository.list_student_notifications(user_id, filters)
        attachments = self.repository.get_attachments_by_message_ids(
            [row.idMensagem for row in rows]
        )

        return [
            {
                "id": row.idMensagem,
                "titulo": row.tituloMensagem,
                "descricao": row.descricaoMensagem,
                "data": str(row.dataMensagem) if row.dataMensagem else None,
                "categoria": row.categoria,
                "prioridade": row.prioridade,
                "materia": row.nomeMateria,
                "dataLimite": str(row.dataLimite) if row.dataLimite else None,
                "permitirAtraso": (
                    bool(row.permitirAtraso)
                    if row.permitirAtraso is not None
                    else False
                ),
                "lida": bool(row.lida),
                "dataLeitura": str(row.dataLeitura) if row.dataLeitura else None,
                "entregue": bool(row.entregue) if row.entregue is not None else False,
                "atrasada": bool(row.atrasada) if row.atrasada is not None else False,
                "bloqueada": bool(row.bloqueada) if row.bloqueada is not None else False,
                "dataEnvio": str(row.dataEnvio) if row.dataEnvio else None,
                "nota": float(row.nota) if row.nota is not None else None,
                "comentarioProfessor": row.comentarioProfessor,
                "corrigida": bool(row.corrigida) if row.corrigida is not None else False,
                "anexos": attachments.get(row.idMensagem, []),
            }
            for row in rows
        ]

    def confirm_read(self, message_id: int, user_id: int) -> dict:
        self.repository.confirm_read(message_id, user_id)
        self.db.commit()
        return {"success": True}

    def mark_all_read(self, user_id: int) -> dict:
        self.repository.mark_all_read(user_id)
        self.db.commit()
        return {"success": True}

    def get_dashboard(self, user_id: int) -> dict:
        result = self.repository.get_dashboard(user_id)
        return {
            "totalMensagens": result.totalMensagens or 0,
            "naoLidas": result.naoLidas or 0,
            "entregues": result.entregues or 0,
            "atrasadas": result.atrasadas or 0,
        }

    def get_user_summary(self, user_id: int) -> dict:
        result = self.repository.get_user_summary(user_id)

        if not result:
            return {"nome": "Usuario", "turma": ""}

        return {
            "nome": result.nomeUser,
            "turma": result.nomeClasse if result.nomeClasse else "",
        }

    def send_delivery(
        self,
        message_id: int,
        student_id: int,
        observation: str | None,
        files: list[UploadFile],
    ) -> dict:
        delivery = self.repository.get_delivery(message_id, student_id)

        if not delivery:
            raise HTTPException(status_code=404, detail="Entrega nao encontrada")
        if delivery.bloqueada:
            raise HTTPException(status_code=403, detail="Entrega bloqueada")

        deadline = self.repository.get_message_deadline(message_id)
        late = False
        if deadline.dataLimite:
            late = datetime.now() > deadline.dataLimite
            if late and not deadline.permitirAtraso:
                raise HTTPException(status_code=403, detail="Prazo encerrado")

        self.repository.update_delivery(delivery.idEntrega, late, observation)
        for file in files:
            content = file.file.read()
            self.repository.add_delivery_file(
                delivery.idEntrega,
                file.filename,
                file.content_type,
                content,
            )

        self.db.commit()
        return {"success": True, "atrasada": late}

    def _save_message_attachments(
        self,
        message_id: int,
        arquivos: list[UploadFile],
    ) -> list[dict]:
        saved_attachments = []
        for arquivo in arquivos:
            content = arquivo.file.read()
            filename = arquivo.filename or "arquivo"
            if len(content) > MAX_ATTACHMENT_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"O arquivo {filename} excede 10 MB",
                )

            attachment_id = self.repository.add_message_attachment(
                message_id,
                filename,
                arquivo.content_type,
                content,
            )
            saved_attachments.append({
                "id": attachment_id,
                "nome": filename,
                "tipo": arquivo.content_type,
                "tamanho": len(content),
            })
        return saved_attachments

    def _validate_existing_ids(self, target: str, ids: list[int]) -> None:
        if not ids:
            return

        table, column = VALIDATION_TARGETS[target]
        existing_ids = self.repository.get_existing_ids(table, column, ids)
        missing_ids = sorted(set(ids) - existing_ids)
        if missing_ids:
            raise HTTPException(
                status_code=422,
                detail=f"{target} inexistente(s): {missing_ids}",
            )

    @staticmethod
    def _validate_notification_data(
        titulo: str,
        descricao: str,
        categoria: str,
        prioridade: str,
        class_ids: list[int],
        direct_student_ids: list[int],
        agendada: bool,
        scheduled_at,
        deadline,
    ) -> None:
        if not titulo or len(titulo) > 150:
            raise HTTPException(
                status_code=422,
                detail="O titulo deve ter entre 1 e 150 caracteres",
            )
        if not descricao or len(descricao) > 600:
            raise HTTPException(
                status_code=422,
                detail="A descricao deve ter entre 1 e 600 caracteres",
            )
        if categoria not in {"AVISO", "ATIVIDADE"}:
            raise HTTPException(status_code=422, detail="Categoria invalida")
        if prioridade not in {"BAIXA", "NORMAL", "ALTA", "URGENTE"}:
            raise HTTPException(status_code=422, detail="Prioridade invalida")
        if not class_ids and not direct_student_ids:
            raise HTTPException(
                status_code=422,
                detail="Selecione ao menos uma turma ou um aluno",
            )
        if agendada and not scheduled_at:
            raise HTTPException(status_code=422, detail="Informe a data de agendamento")
        if agendada and scheduled_at and scheduled_at <= datetime.now():
            raise HTTPException(
                status_code=422,
                detail="A data de agendamento deve estar no futuro",
            )
        if categoria == "ATIVIDADE" and not deadline:
            raise HTTPException(
                status_code=422,
                detail="Atividades precisam de uma data limite",
            )
        if deadline and scheduled_at and deadline <= scheduled_at:
            raise HTTPException(
                status_code=422,
                detail="A data limite deve ser posterior ao agendamento",
            )
