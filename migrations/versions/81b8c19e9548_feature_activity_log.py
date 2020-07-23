"""feature/activity_log

Revision ID: 81b8c19e9548
Revises:
Create Date: 2020-07-23 00:35:07.536608

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81b8c19e9548'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("account_changes") as batch_op:
        batch_op.add_column(sa.Column('new_value_str', sa.String(length=60), nullable=True))
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_user_change", 'users', ['user_id'], ['id'])
    # ### commands auto generated by Alembic - please adjust! ###
    # op.add_column('account_changes', sa.Column('new_value_str', sa.String(length=60), nullable=True))
    # op.add_column('account_changes', sa.Column('user_id', sa.Integer(), nullable=True))
    # op.create_foreign_key(None, 'account_changes', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table("account_changes") as batch_op:
        batch_op.drop_constraint("fk_user_change", type_='foreignkey')
        batch_op.drop_column('user_id')
        batch_op.drop_column('new_value_str')

    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_constraint(None, 'account_changes', type_='foreignkey')
    # op.drop_column('account_changes', 'user_id')
    # op.drop_column('account_changes', 'new_value_str')
    # ### end Alembic commands ###