from typing import Any


def success(data: Any, message: str = "Success") -> dict:
    return {"success": True, "message": message, "data": data}


def error(message: str, code: int = 400) -> dict:
    return {"success": False, "message": message, "code": code}
