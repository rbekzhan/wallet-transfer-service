from decimal import Decimal


class RateServiceMock:
    """
    Простой мок для курсов валют.
    Используется вместо таблицы rates или внешнего API.
    """

    def __init__(self):
        # mock-курсы (1 base = value quote)
        self.rates = {
            ("USD", "EUR"): Decimal("0.92"),
            ("EUR", "USD"): Decimal("1.087"),
            ("USD", "KZT"): Decimal("495"),
            ("KZT", "USD"): Decimal("0.00202"),
            ("EUR", "KZT"): Decimal("530"),
            ("KZT", "EUR"): Decimal("0.00188"),
        }

    async def get_rate(self, base: str, quote: str) -> Decimal:
        base, quote = base.upper(), quote.upper()
        if base == quote:
            return Decimal("1")
        return self.rates.get((base, quote), Decimal("1"))
