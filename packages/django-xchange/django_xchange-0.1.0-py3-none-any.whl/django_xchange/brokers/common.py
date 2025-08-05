import typing
from decimal import Decimal

from django_xchange.config import Config
from django_xchange.models import get_base_currency
from django_xchange.utils import resolve_fqn
from exceptions import ConfigurationError

if typing.TYPE_CHECKING:
    from datetime import date


class BaseBroker:
    def get_rates(self, day: 'date', symbols: list[str]) -> dict[str, Decimal]:
        raise NotImplementedError()


class Broker:
    def get_rates(self, day: 'date', symbols: list[str] = None) -> dict[str, Decimal]:
        if not (brokers := Config().BROKERS):
            raise ConfigurationError('No brokers configured')
        for broker in brokers:
            try:
                resolved = resolve_fqn(broker)()
                res = resolved.get_rates(day, symbols)
                base = get_base_currency()
                if base != res['base']:
                    ratio = round(Decimal(1 / res['rates'][base]), 8)
                    rates = {k: float(round(v * ratio, 6)) for k, v in res['rates'].items()}
                return rates
            except Exception:  # noqa: BLE001, S110
                # TODO: think of better handling
                pass
        raise RuntimeError('No rates available')
