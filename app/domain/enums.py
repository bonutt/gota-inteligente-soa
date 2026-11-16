"""Enumerações do domínio Gota Inteligente."""
from enum import Enum


class AcaoIrrigacao(str, Enum):
    IRRIGAR = "IRRIGAR"
    NAO_IRRIGAR = "NAO_IRRIGAR"
    AGUARDAR_CHUVA = "AGUARDAR_CHUVA"


class OrigemRecomendacao(str, Enum):
    REGRAS = "REGRAS"   # decisão do motor de regras desta API
    IA = "IA"           # decisão enviada pelo modelo de ML (Python)
    MANUAL = "MANUAL"   # decisão do próprio agricultor/técnico


class TipoAlerta(str, Enum):
    ESTRESSE_HIDRICO = "ESTRESSE_HIDRICO"
    CHUVA_PREVISTA = "CHUVA_PREVISTA"
    SOLO_ENCHARCADO = "SOLO_ENCHARCADO"


class Severidade(str, Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class NivelEstresse(str, Enum):
    NORMAL = "NORMAL"
    ATENCAO = "ATENCAO"
    CRITICO = "CRITICO"
    SEM_DADOS = "SEM_DADOS"
