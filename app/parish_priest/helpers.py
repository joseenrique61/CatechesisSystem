from datetime import date
from typing import Optional


def calculate_age(born_date: Optional[date]) -> Optional[int]:
    if not born_date:
        return None
    today = date.today()
    return today.year - born_date.year - ((today.month, today.day) < (born_date.month, born_date.day))