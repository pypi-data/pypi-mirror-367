from django.conf import settings


_DEFAULT_SETTINGS = {'BASE_CURRENCY': 'EUR', 'CURRENCIES': ['USD', 'EUR', 'GBP'], 'BROKERS': []}


class Config:
    def __init__(self) -> None:
        self.conf = _DEFAULT_SETTINGS | getattr(settings, 'DJANGO_XCHANGE', {})
        for x, v in self.conf.items():
            if callable(v):
                self.conf[x] = v()

    def __getattr__(self, item: str) -> object:
        if item in self.conf:
            return self.conf[item]
        raise AttributeError(item)
