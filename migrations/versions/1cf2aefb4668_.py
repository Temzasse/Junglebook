"""empty message

Revision ID: 1cf2aefb4668
Revises: 4c670f50fd04
Create Date: 2015-02-08 17:33:41.029251

"""

# revision identifiers, used by Alembic.
revision = '1cf2aefb4668'
down_revision = '4c670f50fd04'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reveivers',
    sa.Column('giver_id', sa.Integer(), nullable=True),
    sa.Column('receiver_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['giver_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['receiver_id'], ['user.id'], )
    )
    op.drop_table('followers')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('followers',
    sa.Column('friend_a_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('friend_b_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['friend_a_id'], [u'user.id'], name=u'followers_friend_a_id_fkey'),
    sa.ForeignKeyConstraint(['friend_b_id'], [u'user.id'], name=u'followers_friend_b_id_fkey')
    )
    op.drop_table('reveivers')
    ### end Alembic commands ###