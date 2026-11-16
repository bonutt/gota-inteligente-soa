"""Entidades do domínio (mapeadas para tabelas com SQLAlchemy 2.0).

Produtor 1──N Propriedade 1──N Dispositivo 1──N LeituraSensor
                    │
                    ├──N Recomendacao (decisão de irrigar ou não)
                    └──N Alerta       (avisos para o agricultor e para o painel)
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.enums import AcaoIrrigacao, OrigemRecomendacao, Severidade, TipoAlerta


def agora() -> datetime:
    return datetime.now(timezone.utc)


class Produtor(Base):
    """Agricultor familiar atendido pela solução."""

    __tablename__ = "produtores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    telefone: Mapped[str | None] = mapped_column(String(20))
    municipio: Mapped[str] = mapped_column(String(80), index=True)
    uf: Mapped[str] = mapped_column(String(2))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

    propriedades: Mapped[list["Propriedade"]] = relationship(
        back_populates="produtor", cascade="all, delete-orphan"
    )


class Propriedade(Base):
    """Sítio/fazenda onde o kit Gota Inteligente está instalado."""

    __tablename__ = "propriedades"
    __table_args__ = (
        CheckConstraint("area_hectares > 0", name="area_positiva"),
        CheckConstraint("umidade_minima_ideal < umidade_maxima_ideal", name="faixa_umidade_valida"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    produtor_id: Mapped[int] = mapped_column(ForeignKey("produtores.id", ondelete="CASCADE"), index=True)
    nome: Mapped[str] = mapped_column(String(120))
    municipio: Mapped[str] = mapped_column(String(80), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    area_hectares: Mapped[float] = mapped_column(Float)
    cultura: Mapped[str] = mapped_column(String(60))
    umidade_minima_ideal: Mapped[float] = mapped_column(Float, default=35.0)
    umidade_maxima_ideal: Mapped[float] = mapped_column(Float, default=70.0)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

    produtor: Mapped[Produtor] = relationship(back_populates="propriedades")
    dispositivos: Mapped[list["Dispositivo"]] = relationship(
        back_populates="propriedade", cascade="all, delete-orphan"
    )
    recomendacoes: Mapped[list["Recomendacao"]] = relationship(
        back_populates="propriedade", cascade="all, delete-orphan"
    )
    alertas: Mapped[list["Alerta"]] = relationship(
        back_populates="propriedade", cascade="all, delete-orphan"
    )


class Dispositivo(Base):
    """Kit ESP32 instalado na propriedade (sensor de solo + relé da bomba)."""

    __tablename__ = "dispositivos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True)
    propriedade_id: Mapped[int] = mapped_column(ForeignKey("propriedades.id", ondelete="CASCADE"), index=True)
    descricao: Mapped[str | None] = mapped_column(String(200))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    ultima_comunicacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

    propriedade: Mapped[Propriedade] = relationship(back_populates="dispositivos")
    leituras: Mapped[list["LeituraSensor"]] = relationship(
        back_populates="dispositivo", cascade="all, delete-orphan"
    )


class LeituraSensor(Base):
    """Telemetria enviada pelo ESP32."""

    __tablename__ = "leituras_sensor"
    __table_args__ = (
        CheckConstraint("umidade_solo BETWEEN 0 AND 100", name="umidade_solo_percentual"),
        CheckConstraint("probabilidade_chuva BETWEEN 0 AND 100", name="chuva_percentual"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dispositivo_id: Mapped[int] = mapped_column(ForeignKey("dispositivos.id", ondelete="CASCADE"), index=True)
    umidade_solo: Mapped[float] = mapped_column(Float)
    temperatura_ar: Mapped[float] = mapped_column(Float)
    umidade_ar: Mapped[float] = mapped_column(Float)
    probabilidade_chuva: Mapped[float] = mapped_column(Float)
    bomba_ligada: Mapped[bool] = mapped_column(Boolean, default=False)
    # Adicionada na migração 0003 (índice de estresse hídrico calculado pela API)
    indice_estresse: Mapped[int | None] = mapped_column(Integer)
    registrada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, index=True)

    dispositivo: Mapped[Dispositivo] = relationship(back_populates="leituras")


class Recomendacao(Base):
    """Decisão de irrigação (das regras da API, do modelo de IA ou manual)."""

    __tablename__ = "recomendacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    propriedade_id: Mapped[int] = mapped_column(ForeignKey("propriedades.id", ondelete="CASCADE"), index=True)
    leitura_id: Mapped[int | None] = mapped_column(ForeignKey("leituras_sensor.id", ondelete="SET NULL"))
    acao: Mapped[AcaoIrrigacao] = mapped_column(SAEnum(AcaoIrrigacao, name="acao_irrigacao", native_enum=False, length=20))
    origem: Mapped[OrigemRecomendacao] = mapped_column(
        SAEnum(OrigemRecomendacao, name="origem_recomendacao", native_enum=False, length=10)
    )
    motivo: Mapped[str] = mapped_column(Text)
    confianca: Mapped[float | None] = mapped_column(Float)  # usado quando vem da IA (0 a 1)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, index=True)

    propriedade: Mapped[Propriedade] = relationship(back_populates="recomendacoes")


class Alerta(Base):
    """Aviso gerado para o agricultor (app) e para o painel da prefeitura/sindicato."""

    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    propriedade_id: Mapped[int] = mapped_column(ForeignKey("propriedades.id", ondelete="CASCADE"), index=True)
    tipo: Mapped[TipoAlerta] = mapped_column(SAEnum(TipoAlerta, name="tipo_alerta", native_enum=False, length=20))
    severidade: Mapped[Severidade] = mapped_column(SAEnum(Severidade, name="severidade", native_enum=False, length=10))
    mensagem: Mapped[str] = mapped_column(Text)
    lido: Mapped[bool] = mapped_column(Boolean, default=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, index=True)

    propriedade: Mapped[Propriedade] = relationship(back_populates="alertas")
