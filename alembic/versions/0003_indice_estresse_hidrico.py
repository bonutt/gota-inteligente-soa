"""Adiciona o índice de estresse hídrico (0 a 100) em cada leitura do sensor.

Evolução do modelo: o painel regional (C#) precisava do índice já calculado
para não recalcular a cada consulta.

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-16
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("leituras_sensor") as batch:
        batch.add_column(sa.Column("indice_estresse", sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("leituras_sensor") as batch:
        batch.drop_column("indice_estresse")
