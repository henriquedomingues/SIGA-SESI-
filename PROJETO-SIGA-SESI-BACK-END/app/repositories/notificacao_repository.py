from sqlalchemy import text
from sqlalchemy.orm import Session


class NotificacaoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_configurations(self) -> dict:
        classes = self.db.execute(text("""
            SELECT c.idClasseDeAula AS id, c.nomeClasse AS nome, c.anoLetivo,
                   c.idEscola, COUNT(a.idUser) AS totalAlunos
            FROM tblClasseDeAula c
            LEFT JOIN tblAluno a ON a.idClasseDeAula = c.idClasseDeAula
            GROUP BY c.idClasseDeAula, c.nomeClasse, c.anoLetivo, c.idEscola
            ORDER BY c.anoLetivo DESC, c.nomeClasse
        """)).mappings().all()

        materias = self.db.execute(text("""
            SELECT idMateria AS id, nomeMateria AS nome
            FROM tblMateria
            ORDER BY nomeMateria
        """)).mappings().all()

        alunos = self.db.execute(text("""
            SELECT a.idUser AS id, u.nomeUser AS nome, a.idClasseDeAula,
                   c.nomeClasse AS turma
            FROM tblAluno a
            JOIN tblUser u ON u.idUser = a.idUser
            LEFT JOIN tblClasseDeAula c ON c.idClasseDeAula = a.idClasseDeAula
            ORDER BY u.nomeUser
        """)).mappings().all()

        professores = self.db.execute(text("""
            SELECT p.idUser AS id, u.nomeUser AS nome
            FROM tblProfessor p
            JOIN tblUser u ON u.idUser = p.idUser
            ORDER BY u.nomeUser
        """)).mappings().all()

        return {
            "classes": [dict(row) for row in classes],
            "materias": [dict(row) for row in materias],
            "alunos": [dict(row) for row in alunos],
            "professores": [dict(row) for row in professores],
        }

    def list_created(self, limit: int):
        return self.db.execute(text("""
            SELECT m.idMensagem AS id, m.tituloMensagem AS titulo,
                   m.descricaoMensagem AS descricao, m.dataMensagem,
                   m.idMateria, mat.nomeMateria AS materia, m.idClasseDeAula,
                   c.nomeClasse AS turmaPrincipal, m.idProfessor,
                   u.nomeUser AS professor, m.categoria, m.prioridade,
                   m.solicitarConfirmacaoLeitura, m.agendada, m.dataAgendamento,
                   m.publicada, m.dataLimite, m.permitirAtraso, m.ativa,
                   COUNT(DISTINCT ma.idUser) AS totalDestinatarios,
                   COUNT(DISTINCT mc.idClasseDeAula) AS totalTurmas,
                   COUNT(DISTINCT an.idAnexo) AS totalAnexos
            FROM tblMensagem m
            LEFT JOIN tblMateria mat ON mat.idMateria = m.idMateria
            LEFT JOIN tblClasseDeAula c ON c.idClasseDeAula = m.idClasseDeAula
            LEFT JOIN tblProfessor p ON p.idUser = m.idProfessor
            LEFT JOIN tblUser u ON u.idUser = p.idUser
            LEFT JOIN tblMensagemAluno ma ON ma.idMensagem = m.idMensagem
            LEFT JOIN tblMensagemClasse mc ON mc.idMensagem = m.idMensagem
            LEFT JOIN tblAnexo an ON an.idMensagem = m.idMensagem
            GROUP BY m.idMensagem, m.tituloMensagem, m.descricaoMensagem,
                     m.dataMensagem, m.idMateria, mat.nomeMateria,
                     m.idClasseDeAula, c.nomeClasse, m.idProfessor, u.nomeUser,
                     m.categoria, m.prioridade, m.solicitarConfirmacaoLeitura,
                     m.agendada, m.dataAgendamento, m.publicada, m.dataLimite,
                     m.permitirAtraso, m.ativa
            ORDER BY m.idMensagem DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()

    def get_existing_ids(self, table: str, column: str, ids: list[int]) -> set[int]:
        if not ids:
            return set()

        placeholders = ", ".join(f":id_{index}" for index in range(len(ids)))
        params = {f"id_{index}": value for index, value in enumerate(ids)}
        rows = self.db.execute(
            text(f"SELECT {column} FROM {table} WHERE {column} IN ({placeholders})"),
            params,
        ).fetchall()
        return {int(row[0]) for row in rows}

    def create_message(self, values: dict) -> int:
        result = self.db.execute(text("""
            INSERT INTO tblMensagem (
                tituloMensagem, descricaoMensagem, idMateria, idClasseDeAula,
                idProfessor, categoria, prioridade, solicitarConfirmacaoLeitura,
                agendada, dataAgendamento, publicada, dataLimite, permitirAtraso,
                ativa
            ) VALUES (
                :titulo, :descricao, :idMateria, :idClasseDeAula, :idProfessor,
                :categoria, :prioridade, :solicitarConfirmacaoLeitura,
                :agendada, :dataAgendamento, :publicada, :dataLimite,
                :permitirAtraso, :ativa
            )
        """), values)
        return int(result.lastrowid)

    def add_message_class(self, message_id: int, class_id: int) -> None:
        self.db.execute(text("""
            INSERT INTO tblMensagemClasse (idMensagem, idClasseDeAula)
            VALUES (:idMensagem, :idClasseDeAula)
        """), {"idMensagem": message_id, "idClasseDeAula": class_id})

    def get_student_ids_by_class_ids(self, class_ids: list[int]) -> set[int]:
        if not class_ids:
            return set()

        placeholders = ", ".join(f":class_{index}" for index in range(len(class_ids)))
        params = {f"class_{index}": value for index, value in enumerate(class_ids)}
        rows = self.db.execute(text(f"""
            SELECT idUser
            FROM tblAluno
            WHERE idClasseDeAula IN ({placeholders})
        """), params).fetchall()
        return {int(row.idUser) for row in rows}

    def upsert_message_student(
        self,
        message_id: int,
        student_id: int,
        direct_recipient: bool,
    ) -> None:
        self.db.execute(text("""
            INSERT INTO tblMensagemAluno (idMensagem, idUser, destinatarioDireto)
            VALUES (:idMensagem, :idUser, :destinatarioDireto)
            ON DUPLICATE KEY UPDATE destinatarioDireto = VALUES(destinatarioDireto)
        """), {
            "idMensagem": message_id,
            "idUser": student_id,
            "destinatarioDireto": direct_recipient,
        })

    def add_message_attachment(
        self,
        message_id: int,
        filename: str,
        content_type: str | None,
        content: bytes,
    ) -> int:
        result = self.db.execute(text("""
            INSERT INTO tblAnexo (
                idMensagem, nomeArquivo, tipoArquivo, tamanhoArquivo, arquivo
            ) VALUES (
                :idMensagem, :nomeArquivo, :tipoArquivo, :tamanhoArquivo, :arquivo
            )
        """), {
            "idMensagem": message_id,
            "nomeArquivo": filename,
            "tipoArquivo": content_type,
            "tamanhoArquivo": len(content),
            "arquivo": content,
        })
        return int(result.lastrowid)

    def list_student_notifications(self, user_id: int, filters: dict):
        query = """
            SELECT m.idMensagem, m.tituloMensagem, m.descricaoMensagem,
                   m.dataMensagem, m.categoria, m.prioridade, m.dataLimite,
                   m.permitirAtraso, ma.lida, ma.dataLeitura, e.idEntrega,
                   e.entregue, e.atrasada, e.bloqueada, e.dataEnvio, e.nota,
                   e.comentarioProfessor, e.corrigida,
                   COALESCE(mat.nomeMateria,'Geral') AS nomeMateria
            FROM tblMensagem m
            JOIN tblMensagemAluno ma ON ma.idMensagem = m.idMensagem
            LEFT JOIN tblMateria mat ON mat.idMateria = m.idMateria
            LEFT JOIN tblEntregaAtividade e
                ON e.idMensagem = m.idMensagem AND e.idAluno = ma.idUser
            WHERE ma.idUser = :id_user
              AND m.ativa = TRUE
              AND (
                    m.publicada = TRUE
                    OR (m.agendada = TRUE AND m.dataAgendamento <= NOW())
              )
        """
        params = {"id_user": user_id}

        if filters.get("status") == "read":
            query += " AND ma.lida = TRUE"
        elif filters.get("status") == "unread":
            query += " AND ma.lida = FALSE"

        all_subjects_labels = {"Todas as materias", "Todas as mat\u00e9rias"}
        if filters.get("materia") and filters["materia"] not in all_subjects_labels:
            query += " AND COALESCE(mat.nomeMateria,'Geral') = :materia"
            params["materia"] = filters["materia"]

        if filters.get("categoria"):
            query += " AND m.categoria = :categoria"
            params["categoria"] = filters["categoria"]

        if filters.get("prioridade"):
            query += " AND m.prioridade = :prioridade"
            params["prioridade"] = filters["prioridade"]

        if filters.get("dateFrom"):
            query += " AND DATE(m.dataMensagem) >= :dateFrom"
            params["dateFrom"] = filters["dateFrom"]

        if filters.get("dateTo"):
            query += " AND DATE(m.dataMensagem) <= :dateTo"
            params["dateTo"] = filters["dateTo"]

        query += """
            ORDER BY CASE m.prioridade
                WHEN 'URGENTE' THEN 1
                WHEN 'ALTA' THEN 2
                WHEN 'NORMAL' THEN 3
                WHEN 'BAIXA' THEN 4
            END, m.dataMensagem DESC
        """

        if filters.get("limit"):
            query += " LIMIT :limit"
            params["limit"] = int(filters["limit"])

        return self.db.execute(text(query), params).fetchall()

    def get_attachments_by_message_ids(self, message_ids: list[int]) -> dict[int, list]:
        if not message_ids:
            return {}

        placeholders = ", ".join(f":id_{index}" for index in range(len(message_ids)))
        params = {f"id_{index}": value for index, value in enumerate(message_ids)}
        rows = self.db.execute(text(f"""
            SELECT idAnexo, idMensagem, nomeArquivo, tipoArquivo
            FROM tblanexo
            WHERE idMensagem IN ({placeholders})
        """), params).fetchall()

        attachments = {}
        for row in rows:
            attachments.setdefault(row.idMensagem, []).append({
                "idAnexo": row.idAnexo,
                "nome": row.nomeArquivo,
                "tipo": row.tipoArquivo,
            })
        return attachments

    def confirm_read(self, message_id: int, user_id: int) -> None:
        self.db.execute(text("""
            UPDATE tblMensagemAluno
            SET lida = TRUE, dataLeitura = NOW()
            WHERE idMensagem = :idMensagem AND idUser = :idUser
        """), {"idMensagem": message_id, "idUser": user_id})

    def mark_all_read(self, user_id: int) -> None:
        self.db.execute(text("""
            UPDATE tblMensagemAluno
            SET lida = TRUE, dataLeitura = NOW()
            WHERE idUser = :idUser
        """), {"idUser": user_id})

    def get_dashboard(self, user_id: int):
        return self.db.execute(text("""
            SELECT COUNT(*) totalMensagens,
                   SUM(CASE WHEN ma.lida = FALSE THEN 1 ELSE 0 END) naoLidas,
                   SUM(CASE WHEN e.entregue = TRUE THEN 1 ELSE 0 END) entregues,
                   SUM(CASE WHEN e.atrasada = TRUE THEN 1 ELSE 0 END) atrasadas
            FROM tblMensagemAluno ma
            LEFT JOIN tblEntregaAtividade e
                ON e.idMensagem = ma.idMensagem AND e.idAluno = ma.idUser
            WHERE ma.idUser = :idUser
        """), {"idUser": user_id}).fetchone()

    def get_user_summary(self, user_id: int):
        return self.db.execute(text("""
            SELECT u.nomeUser, c.nomeClasse
            FROM tblUser u
            LEFT JOIN tblAluno a ON a.idUser = u.idUser
            LEFT JOIN tblClasseDeAula c ON c.idClasseDeAula = a.idClasseDeAula
            WHERE u.idUser = :id_user
        """), {"id_user": user_id}).fetchone()

    def get_delivery(self, message_id: int, student_id: int):
        return self.db.execute(text("""
            SELECT idEntrega, bloqueada
            FROM tblentregaatividade
            WHERE idMensagem = :idMensagem AND idAluno = :idAluno
        """), {"idMensagem": message_id, "idAluno": student_id}).fetchone()

    def get_message_deadline(self, message_id: int):
        return self.db.execute(text("""
            SELECT dataLimite, permitirAtraso
            FROM tblmensagem
            WHERE idMensagem = :id
        """), {"id": message_id}).fetchone()

    def update_delivery(self, delivery_id: int, late: bool, observation: str | None):
        self.db.execute(text("""
            UPDATE tblentregaatividade SET
                entregue = TRUE,
                atrasada = :atrasada,
                observacaoAluno = :obs,
                dataEnvio = NOW()
            WHERE idEntrega = :idEntrega
        """), {"atrasada": late, "obs": observation, "idEntrega": delivery_id})

    def add_delivery_file(
        self,
        delivery_id: int,
        filename: str | None,
        content_type: str | None,
        content: bytes,
    ) -> None:
        self.db.execute(text("""
            INSERT INTO tblarquivoentrega (
                idEntrega, nomeArquivo, tipoArquivo, tamanhoArquivo, arquivo
            ) VALUES (
                :idEntrega, :nome, :tipo, :tamanho, :arquivo
            )
        """), {
            "idEntrega": delivery_id,
            "nome": filename,
            "tipo": content_type,
            "tamanho": len(content),
            "arquivo": content,
        })
