from decimal import Decimal

from django.conf import settings
from pyoxr import OXRClient, init
from django_xchange.brokers.common import BaseBroker
import typing


if typing.TYPE_CHECKING:
    from datetime import date


class PyoxrBroker(BaseBroker):
    _initialised = False

    def __init__(self, **kwargs) -> None:
        if not PyoxrBroker._initialised:
            init(settings.OPEN_EXCHANGE_RATES_APP_ID)
            PyoxrBroker._initialised = True

    def get_rates(self, day: 'date', symbols: list[str]) -> dict[str, typing.Any]:
        client = OXRClient(settings.OPEN_EXCHANGE_RATES_APP_ID)
        res = client.get_historical(date=day.strftime('%Y-%m-%d'), symbols=','.join(sorted(symbols)))
        return {'base': res['base'], 'rates': {k: Decimal(str(v)) for k, v in res['rates'].items()}}
