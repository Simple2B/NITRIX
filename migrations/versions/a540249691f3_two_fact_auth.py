"""two-fact-auth

Revision ID: a540249691f3
Revises: 81b8c19e9548
Create Date: 2020-07-24 21:33:14.983988

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a540249691f3'
down_revision = '81b8c19e9548'
branch_labels = None
depends_on = None


def upgrade():
    from app.models import User
    # using batch operations for support SQLite
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column('otp_active', sa.Boolean(), default=False))
        batch_op.add_column(sa.Column('otp_secret', sa.String(length=32)))

    for u in User.query.all():
        u.otp_secret = User.gen_secret()
        u.save()
    # ### commands auto generated by Alembic - please adjust! ###
    # op.add_column('users', sa.Column('otp_active', sa.Boolean(), nullable=True))
    # op.add_column('users', sa.Column('otp_secret', sa.String(length=16), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # using batch operations for support SQLite
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column('otp_secret')
        batch_op.drop_column('otp_active')
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_column('users', 'otp_secret')
    # op.drop_column('users', 'otp_active')
    # ### end Alembic commands ###