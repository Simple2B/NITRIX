"""empty message

Revision ID: 371cd17ac7d8
Revises: 
Create Date: 2021-11-18 11:53:19.922116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "371cd17ac7d8"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "phones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=False),
        sa.Column(
            "status", sa.Enum("active", "not_active", name="status"), nullable=True
        ),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.Column("ninja_product_id", sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=False),
        sa.Column(
            "status", sa.Enum("active", "not_active", name="status"), nullable=True
        ),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "resellers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=False),
        sa.Column(
            "status", sa.Enum("active", "not_active", name="status"), nullable=True
        ),
        sa.Column("comments", sa.String(length=256), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.Column("last_activity", sa.DateTime(), nullable=True),
        sa.Column("ninja_client_id", sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=False),
        sa.Column(
            "user_type",
            sa.Enum("super_admin", "admin", "user", name="type"),
            nullable=True,
        ),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column(
            "activated", sa.Enum("active", "not_active", name="status"), nullable=True
        ),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.Column("otp_secret", sa.String(length=32), nullable=True),
        sa.Column("otp_active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("phone_id", sa.Integer(), nullable=True),
        sa.Column("reseller_id", sa.Integer(), nullable=True),
        sa.Column("sim", sa.String(length=20), nullable=True),
        sa.Column("imei", sa.String(length=60), nullable=True),
        sa.Column("comment", sa.String(length=256), nullable=True),
        sa.Column("activation_date", sa.DateTime(), nullable=True),
        sa.Column("months", sa.Integer(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["phone_id"],
            ["phones.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["reseller_id"],
            ["resellers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "history_changes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column(
            "change_type",
            sa.Enum(
                "creation_account",
                "deletion_account",
                "changes_account",
                "extension_account_new",
                "extensions_account_change",
                "extensions_account_delete",
                "creation_reseller",
                "deletion_reseller",
                "changes_reseller",
                "creation_product",
                "deletion_product",
                "changes_product",
                "creation_reseller_product",
                "deletion_reseller_product",
                "changes_reseller_product",
                "creation_phone",
                "changes_phone",
                "deletion_phone",
                name="edittype",
            ),
            nullable=True,
        ),
        sa.Column("value_name", sa.String(length=64), nullable=True),
        sa.Column("before_value_str", sa.String(length=64), nullable=True),
        sa.Column("after_value_str", sa.String(length=64), nullable=True),
        sa.Column("synced", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "reseller_product",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("reseller_id", sa.Integer(), nullable=True),
        sa.Column("months", sa.Integer(), nullable=True),
        sa.Column("init_price", sa.Float(), nullable=True),
        sa.Column("ext_price", sa.Float(), nullable=True),
        sa.Column("ninja_product_id", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["reseller_id"],
            ["resellers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "account_extension",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("extension_date", sa.DateTime(), nullable=True),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("months", sa.Integer(), nullable=True),
        sa.Column("reseller_id", sa.Integer(), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["reseller_id"],
            ["resellers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("account_extension")
    op.drop_table("reseller_product")
    op.drop_table("history_changes")
    op.drop_table("accounts")
    op.drop_table("users")
    op.drop_table("resellers")
    op.drop_table("products")
    op.drop_table("phones")
    # ### end Alembic commands ###
