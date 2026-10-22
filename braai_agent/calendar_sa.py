"""South African seasons, public holidays and special braai days."""
from datetime import date, timedelta


def season(d: date) -> str:
    """Southern-hemisphere seasons as South Africans use them."""
    m = d.month
    if m in (12, 1, 2):
        return "summer"
    if m in (3, 4, 5):
        return "autumn"
    if m in (6, 7, 8):
        return "winter"
    return "spring"


def easter_sunday(year: int) -> date:
    """Anonymous Gregorian algorithm."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + c + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day + 1)


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    d = date(year, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


def special_days(year: int) -> dict:
    """Public holidays plus other days worth a braai post. key = date, value = id."""
    easter = easter_sunday(year)
    days = {
        date(year, 1, 1): "new_year",
        date(year, 2, 14): "valentines",
        date(year, 3, 21): "human_rights_day",
        easter - timedelta(days=2): "good_friday",
        easter + timedelta(days=1): "family_day",
        date(year, 4, 27): "freedom_day",
        date(year, 5, 1): "workers_day",
        _nth_weekday(year, 5, 6, 2): "mothers_day",
        date(year, 6, 16): "youth_day",
        _nth_weekday(year, 6, 6, 3): "fathers_day",
        date(year, 8, 9): "womens_day",
        date(year, 9, 24): "heritage_day",
        date(year, 12, 16): "reconciliation_day",
        date(year, 12, 24): "christmas_eve",
        date(year, 12, 25): "christmas",
        date(year, 12, 26): "day_of_goodwill",
        date(year, 12, 31): "new_years_eve",
    }
    # A public holiday on a Sunday moves to Monday in South Africa.
    for d, name in list(days.items()):
        if d.weekday() == 6 and name not in ("mothers_day", "fathers_day", "valentines",
                                             "christmas_eve", "new_years_eve"):
            days.setdefault(d + timedelta(days=1), name + "_observed")
    return days


def upcoming_special(d: date, lookahead: int = 2):
    """Special day today or within `lookahead` days (we post every 2nd day, so look ahead).

    Returns (id, days_until) or None.
    """
    for offset in range(lookahead + 1):
        target = d + timedelta(days=offset)
        name = special_days(target.year).get(target)
        if name:
            return name.replace("_observed", ""), offset
    return None


def is_payday_weekend(d: date) -> bool:
    """Most South Africans get paid around the 25th. Month-end braai is a thing."""
    return 24 <= d.day <= 28 and d.weekday() in (3, 4, 5)
