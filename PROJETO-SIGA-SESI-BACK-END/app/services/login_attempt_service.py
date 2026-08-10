from datetime import datetime, timedelta

from fastapi import HTTPException, status


MAX_LOGIN_ATTEMPTS = 10
BLOCK_HOURS = 1

login_attempts_by_ip: dict[str, dict] = {}


def verify_ip_block(ip_address: str) -> None:
    record = login_attempts_by_ip.get(ip_address)

    if record and record["blocked_until"] and datetime.utcnow() < record["blocked_until"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas. Tente novamente mais tarde",
        )


def register_failed_attempt(ip_address: str) -> None:
    record = login_attempts_by_ip.get(ip_address)

    if not record:
        login_attempts_by_ip[ip_address] = {
            "attempts": 1,
            "blocked_until": None,
        }
        return

    record["attempts"] += 1

    if record["attempts"] >= MAX_LOGIN_ATTEMPTS:
        record["blocked_until"] = datetime.utcnow() + timedelta(hours=BLOCK_HOURS)


def reset_attempts(ip_address: str) -> None:
    login_attempts_by_ip[ip_address] = {
        "attempts": 0,
        "blocked_until": None,
    }
