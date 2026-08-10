import json
from datetime import datetime

from fastapi import HTTPException


def parse_id_list(raw_value: str | None, field_name: str) -> list[int]:
    if not raw_value:
        return []

    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} deve ser uma lista JSON valida",
        ) from exc

    if not isinstance(value, list):
        raise HTTPException(status_code=422, detail=f"{field_name} deve ser uma lista")

    try:
        return list(dict.fromkeys(int(item) for item in value))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} contem um identificador invalido",
        ) from exc


def parse_datetime(raw_value: str | None, field_name: str) -> datetime | None:
    if not raw_value:
        return None

    try:
        return datetime.fromisoformat(raw_value.replace("Z", "+00:00")).replace(
            tzinfo=None
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} deve conter uma data e hora valida",
        ) from exc
