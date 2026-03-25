from typing import List


def format_route_path(path: List[str]) -> str:
    return " -> ".join(path)


def format_currency(amount: float) -> str:
    return f"${amount:,.2f}"


def safe_upper(value: str) -> str:
    return value.strip().upper()