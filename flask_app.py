#!python
from dateutil.relativedelta import relativedelta
import click
from app import create_app, db, models, forms
from app.models import (
    User,
    Product,
    Reseller,
    ResellerProduct,
    Phone,
    Account,
    AccountExtension,
)
from app.ninja import api as ninja

app = create_app()


# flask cli context setup
@app.shell_context_processor
def get_context():
    """Objects exposed here will be automatically available from the shell."""
    return dict(app=app, db=db, m=models, forms=forms)


def create_database(test_data=False):
    """ build database """

    def add_reseller_product(product, months, initprice, extprice, reseller):
        reseller_product = ResellerProduct(
            months=months,
            init_price=initprice,
            ext_price=extprice,
            product=product,
            reseller=reseller,
        ).save(False)
        product_key = f"{product.name} {months} Months"
        ninja_product = None
        if ninja.configured:
            prods = [prod for prod in ninja.products if not prod.is_deleted]
            for prod in prods:
                if prod.notes == reseller.name and prod.product_key == product_key:
                    ninja_product = prod
                    break
            else:
                ninja_product = ninja.add_product(
                    product_key=product_key, notes=reseller.name, cost=initprice
                )
        if ninja_product:
            reseller_product.ninja_product_id = ninja_product.id
            reseller_product.save(False)

    def add_phone(name, price):
        phone = Phone(name=name, price=price).save(False)
        product_key = f"Phone-{phone.name}"
        ninja_product = None
        if ninja.configured:
            for prod in [prod for prod in ninja.products if not prod.is_deleted]:
                if (
                    prod.notes == "Phone"
                    and prod.product_key == product_key
                    and prod.cost == price
                ):
                    ninja_product = prod
                    break
            else:
                ninja_product = ninja.add_product(
                    product_key=product_key, notes="Phone", cost=price
                )
        if ninja_product:
            phone.ninja_product_id = ninja_product.id
            phone.save(False)

    def add_reseller(name: str, comments: str):
        reseller = Reseller(name=name, comments=comments).save(False)
        ninja_client = None
        if ninja.configured:
            for client in [
                c for c in ninja.clients if not c.is_deleted and c.name == name
            ]:
                ninja_client = client
                break
            else:
                ninja_client = ninja.add_client(name=reseller.name)
        if ninja_client:
            reseller.ninja_client_id = ninja_client.id
        return reseller

    def add_reseller_with_test_products(name: str, comments: str):
        reseller = add_reseller(name=name, comments=comments)
        PRODUCT_NAME = "Gold"
        product = Product.query.filter(Product.name == PRODUCT_NAME).first()
        if not product:
            product = Product(name=PRODUCT_NAME).save(False)
        for months in (1, 3, 6, 12):
            add_reseller_product(
                months=months,
                initprice=round(6.78 * months, 2),
                extprice=round(4.55 * months, 2),
                product=product,
                reseller=reseller,
            )
        if test_data:
            PRODUCT_NAME = "Silver"
            product = Product.query.filter(Product.name == PRODUCT_NAME).first()
            if not product:
                product = Product(name=PRODUCT_NAME).save(False)
            for months in (1, 3, 6, 12):
                add_reseller_product(
                    months=months,
                    initprice=round(4.57 * months, 2),
                    extprice=round(3.84 * months, 2),
                    product=product,
                    reseller=reseller,
                )
            PRODUCT_NAME = "Bronsa"
            product = Product.query.filter(Product.name == PRODUCT_NAME).first()
            if not product:
                product = Product(name=PRODUCT_NAME).save(False)
            for months in (1, 3, 6, 12):
                add_reseller_product(
                    months=months,
                    initprice=round(2.32 * months, 2),
                    extprice=round(2.05 * months, 2),
                    product=product,
                    reseller=reseller,
                )

        return reseller

    db.create_all()
    Phone(name="None", price=0.00).save(False)
    User(
        name="admin",
        password="ZAQ!xsw2",
        user_type=User.Type.super_admin,
        activated=User.Status.active,
    ).save(False)
    User(
        name="user",
        password="user",
        user_type=User.Type.user,
        activated=User.Status.active,
    ).save(False)
    add_reseller_with_test_products(name="NITRIX", comments="Main reseller")
    add_phone(name="Samsung", price=54.00)
    add_phone(name="Nokia", price=38.00)
    add_phone(name="Lg", price=30.00)
    if test_data:
        for n in range(10):
            add_reseller_with_test_products(
                name=f"Reseller {n + 1}", comments=f"Test reseller {n + 1}"
            )
    db.session.commit()


@app.cli.command()
@click.option("--test-data", is_flag=True, help="if include test data")
@click.confirmation_option(prompt="Are you sure?")
def reset_db(test_data=False):
    """Reset the current database."""
    db.drop_all()
    create_database(test_data)


@app.cli.command()
def restore_ninja_db_invoice_items(test_data=False):
    """Restore invoice items in the InvoiceNinja"""
    from tools import restore_invoice_ninja_invoice_items
    restore_invoice_ninja_invoice_items()


@app.cli.command()
def fix_activation_date():
    """Fix wrong activation date"""
    accounts = Account.query.all()
    for account in accounts:
        extensions = AccountExtension.query.filter(
            AccountExtension.account_id == account.id
        ).order_by(AccountExtension.extension_date.asc()).first()
        if extensions:
            if account.activation_date > extensions.extension_date:
                swap_value = account.activation_date - relativedelta(months=extensions.months)
                account.activation_date = extensions.extension_date
                extensions.extension_date = swap_value
                db.session.add(account)
    db.session.commit()


if __name__ == "__main__":
    app.run()
