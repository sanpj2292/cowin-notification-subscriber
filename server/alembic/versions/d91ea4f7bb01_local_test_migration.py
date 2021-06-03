"""local test migration

Revision ID: d91ea4f7bb01
Revises: 
Create Date: 2021-06-02 23:40:22.100060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd91ea4f7bb01'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('push_notifications',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('endpoint', sa.Text(), nullable=True),
    sa.Column('expirationTime', sa.Float(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('p256dh', sa.Text(), nullable=True),
    sa.Column('auth', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_push_notifications_id'), 'push_notifications', ['id'], unique=False)
    op.add_column('subscribers', sa.Column('pushNotificationId', sa.BIGINT(), nullable=True))
    op.create_foreign_key(None, 'subscribers', 'push_notifications', ['pushNotificationId'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'subscribers', type_='foreignkey')
    op.drop_column('subscribers', 'pushNotificationId')
    op.drop_index(op.f('ix_push_notifications_id'), table_name='push_notifications')
    op.drop_table('push_notifications')
    # ### end Alembic commands ###
