"""Grant the requested content pack once to the existing account named Marcin."""
import copy
import logging

from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

REWARD = 'content_pack_20261016'
# Snapshot kept in the migration so later catalog changes cannot alter this grant.
PACK = {
    'knife': 1, 'club': 1, 'machete': 1, 'chainsaw': 1,
    'pistol': 1, 'revolver': 1, 'ak47': 1,
    'jacket': 1, 'leather_jacket': 1, 'scrap_armor': 1,
    'bulletproof_vest': 1, 'heavy_armor': 1, 'exoskeleton': 1,
    'ammo': 100, 'grenade': 5, 'medkit': 5, 'scrap': 1, 'electronics': 1,
}


def grant_pack(connection):
    players = sa.table('players', sa.column('id', sa.String(36)), sa.column('state', sa.JSON()))
    matches = connection.execute(sa.select(players).where(
        sa.func.lower(players.c.state['nickname'].as_string()) == 'marcin'
    ).with_for_update()).mappings().all()
    if len(matches) != 1:
        logging.getLogger('alembic.runtime.migration').warning(
            'Content pack skipped: target nickname must match exactly one existing account (matched %s).', len(matches))
        return False
    player = matches[0]
    state = copy.deepcopy(player['state'])
    rewards = state.setdefault('claimed_rewards', [])
    if REWARD in rewards:
        return False
    for item, quantity in PACK.items():
        state['inventory'][item] = min(9999, state['inventory'].get(item, 0) + quantity)
    rewards.append(REWARD)
    connection.execute(players.update().where(players.c.id == player['id']).values(state=state))
    logging.getLogger('alembic.runtime.migration').info('Requested content pack granted to one existing account.')
    return True


def upgrade():
    grant_pack(op.get_bind())


def downgrade():
    # Inventory may already have been traded or used; never remove earned items.
    pass
