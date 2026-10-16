"""Initial durable player aggregates, sessions, idempotency receipts and rate limits."""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('players', sa.Column('id', sa.String(36), primary_key=True), sa.Column('email', sa.String(254), unique=True, nullable=False), sa.Column('password', sa.String(255), nullable=False), sa.Column('state', sa.JSON(), nullable=False))
    op.create_table('sessions', sa.Column('token', sa.String(64), primary_key=True), sa.Column('player_id', sa.String(36), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False), sa.Column('csrf', sa.String(64), nullable=False), sa.Column('expires', sa.Float(), nullable=False))
    op.create_index('ix_sessions_player_id', 'sessions', ['player_id'])
    op.create_index('ix_sessions_expires', 'sessions', ['expires'])
    op.create_table('receipts', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('player_id', sa.String(36), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False), sa.Column('key', sa.String(80), nullable=False), sa.Column('fingerprint', sa.String(64), nullable=False), sa.Column('response', sa.JSON(), nullable=False), sa.UniqueConstraint('player_id', 'key'))
    op.create_index('ix_receipts_player_id', 'receipts', ['player_id'])
    op.create_table('login_buckets', sa.Column('key', sa.String(64), primary_key=True), sa.Column('attempts', sa.Integer(), nullable=False), sa.Column('expires', sa.Float(), nullable=False))
    op.create_index('ix_login_buckets_expires', 'login_buckets', ['expires'])


def downgrade():
    for name in ['receipts', 'sessions', 'login_buckets', 'players']:
        op.drop_table(name)
