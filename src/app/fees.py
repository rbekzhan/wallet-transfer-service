from decimal import Decimal


# Таблица комиссий по валютным парам
# (base, quote): (фиксированная комиссия, процент)
FEE_TABLE = {
    ("USD", "EUR"): (Decimal("0.50"), Decimal("0.2")),   # 0.50$ + 0.2%
    ("EUR", "USD"): (Decimal("0.50"), Decimal("0.2")),
    ("USD", "KZT"): (Decimal("10.00"), Decimal("0.3")),  # 10 тенге + 0.3%
    ("KZT", "USD"): (Decimal("10.00"), Decimal("0.3")),
    ("EUR", "KZT"): (Decimal("8.00"), Decimal("0.25")),
    ("KZT", "EUR"): (Decimal("8.00"), Decimal("0.25")),
}

# Комиссия по умолчанию (если пары нет в таблице)
DEFAULT_FIXED = Decimal("0.00")
DEFAULT_PERCENT = Decimal("0.00")


def get_fee(base: str, quote: str) -> tuple[Decimal, Decimal]:
    """
    Возвращает (фиксированная_комиссия, процентная_комиссия)
    """
    base, quote = base.upper(), quote.upper()
    return FEE_TABLE.get((base, quote), (DEFAULT_FIXED, DEFAULT_PERCENT))


def calc_fee(amount: Decimal, fixed: Decimal, percent: Decimal) -> Decimal:
    """
    Рассчитывает итоговую сумму комиссии.
    Формула: (amount * percent/100) + fixed
    """
    percent_part = (amount * (percent / Decimal(100))).quantize(Decimal("0.0001"))
    total_fee = percent_part + fixed
    return total_fee.quantize(Decimal("0.0001"))
