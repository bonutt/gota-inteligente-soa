"""Cria as tabelas de cadastro (produtores, propriedades, dispositivos) e de telemetria.

Revision ID: 0001
Revises:
Create Date: 2026-11-16
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "produtores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("telefone", sa.String(20), nullable=True),
        sa.Column("municipio", sa.String(80), nullable=False),
        sa.Column("uf", sa.String(2), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_produtores"),
    )
    op.create_index("ix_produtores_municipio", "produtores", ["municipio"])

    op.create_table(
        "propriedades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("produtor_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("municipio", sa.String(80), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("area_hectares", sa.Float(), nullable=False),
        sa.Column("cultura", sa.String(60), nullable=False),
        sa.Column("umidade_minima_ideal", sa.Float(), nullable=False),
        sa.Column("umidade_maxima_ideal", sa.Float(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("area_hectares > 0", name="ck_propriedades_area_positiva"),
        sa.CheckConstraint("umidade_minima_ideal < umidade_maxima_ideal",
                           name="ck_propriedades_faixa_umidade_valida"),
        sa.ForeignKeyConstraint(["produtor_id"], ["produtores.id"], ondelete="CASCADE",
                                name="fk_propriedades_produtor_id_produtores"),
        sa.PrimaryKeyConstraint("id", name="pk_propriedades"),
    )
    op.create_index("ix_propriedades_produtor_id", "propriedades", ["produtor_id"])
    op.create_index("ix_propriedades_municipio", "propriedades", ["municipio"])

    op.create_table(
        "dispositivos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("codigo", sa.String(40), nullable=False),
        sa.Column("propriedade_id", sa.Integer(), nullable=False),
        sa.Column("descricao", sa.String(200), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("ultima_comunicacao", sa.DateTime(timezone=True), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["propriedade_id"], ["propriedades.id"], ondelete="CASCADE",
                                name="fk_dispositivos_propriedade_id_propriedades"),
        sa.PrimaryKeyConstraint("id", name="pk_dispositivos"),
        sa.UniqueConstraint("codigo", name="uq_dispositivos_codigo"),
    )
    op.create_index("ix_dispositivos_propriedade_id", "dispositivos", ["propriedade_id"])

    op.create_table(
        "leituras_sensor",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dispositivo_id", sa.Integer(), nullable=False),
        sa.Column("umidade_solo", sa.Float(), nullable=False),
        sa.Column("temperatura_ar", sa.Float(), nullable=False),
        sa.Column("umidade_ar", sa.Float(), nullable=False),
        sa.Column("probabilidade_chuva", sa.Float(), nullable=False),
        sa.Column("bomba_ligada", sa.Boolean(), nullable=False),
        sa.Column("registrada_em", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("umidade_solo BETWEEN 0 AND 100", name="ck_leituras_sensor_umidade_solo_percentual"),
        sa.CheckConstraint("probabilidade_chuva BETWEEN 0 AND 100", name="ck_leituras_sensor_chuva_percentual"),
        sa.ForeignKeyConstraint(["dispositivo_id"], ["dispositivos.id"], ondelete="CASCADE",
                                name="fk_leituras_sensor_dispositivo_id_dispositivos"),
        sa.PrimaryKeyConstraint("id", name="pk_leituras_sensor"),
    )
    op.create_index("ix_leituras_sensor_dispositivo_id", "leituras_sensor", ["dispositivo_id"])
    op.create_index("ix_leituras_sensor_registrada_em", "leituras_sensor", ["registrada_em"])


def downgrade() -> None:
    op.drop_table("leituras_sensor")
    op.drop_table("dispositivos")
    op.drop_table("propriedades")
    op.drop_table("produtores")
