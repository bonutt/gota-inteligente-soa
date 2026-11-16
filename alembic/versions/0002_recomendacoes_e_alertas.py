"""Cria as tabelas de recomendações de irrigação e de alertas.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-16
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recomendacoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("propriedade_id", sa.Integer(), nullable=False),
        sa.Column("leitura_id", sa.Integer(), nullable=True),
        sa.Column("acao", sa.Enum("IRRIGAR", "NAO_IRRIGAR", "AGUARDAR_CHUVA", name="acao_irrigacao",
                                  native_enum=False, length=20), nullable=False),
        sa.Column("origem", sa.Enum("REGRAS", "IA", "MANUAL", name="origem_recomendacao",
                                    native_enum=False, length=10), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=False),
        sa.Column("confianca", sa.Float(), nullable=True),
        sa.Column("criada_em", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["propriedade_id"], ["propriedades.id"], ondelete="CASCADE",
                                name="fk_recomendacoes_propriedade_id_propriedades"),
        sa.ForeignKeyConstraint(["leitura_id"], ["leituras_sensor.id"], ondelete="SET NULL",
                                name="fk_recomendacoes_leitura_id_leituras_sensor"),
        sa.PrimaryKeyConstraint("id", name="pk_recomendacoes"),
    )
    op.create_index("ix_recomendacoes_propriedade_id", "recomendacoes", ["propriedade_id"])
    op.create_index("ix_recomendacoes_criada_em", "recomendacoes", ["criada_em"])

    op.create_table(
        "alertas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("propriedade_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.Enum("ESTRESSE_HIDRICO", "CHUVA_PREVISTA", "SOLO_ENCHARCADO", name="tipo_alerta",
                                  native_enum=False, length=20), nullable=False),
        sa.Column("severidade", sa.Enum("BAIXA", "MEDIA", "ALTA", name="severidade",
                                        native_enum=False, length=10), nullable=False),
        sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column("lido", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["propriedade_id"], ["propriedades.id"], ondelete="CASCADE",
                                name="fk_alertas_propriedade_id_propriedades"),
        sa.PrimaryKeyConstraint("id", name="pk_alertas"),
    )
    op.create_index("ix_alertas_propriedade_id", "alertas", ["propriedade_id"])
    op.create_index("ix_alertas_criado_em", "alertas", ["criado_em"])


def downgrade() -> None:
    op.drop_table("alertas")
    op.drop_table("recomendacoes")
