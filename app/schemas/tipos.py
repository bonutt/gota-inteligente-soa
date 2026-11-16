from datetime import datetime, timezone
from typing import Annotated

from pydantic import AfterValidator


def _garantir_utc(valor: datetime) -> datetime:
    # O SQLite não guarda fuso horário; todas as datas são gravadas em UTC.
    return valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)


DataHoraUTC = Annotated[datetime, AfterValidator(_garantir_utc)]
