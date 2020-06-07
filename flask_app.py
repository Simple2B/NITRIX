#!python
import click
from app import create_app, db, models, forms
from app.models import User, Product, Reseller, ResellerProduct, Phone
from app.ninja import api as ninja

app = create_app()


# flask cli context setup
@app.shell_context_processor
def get_context():
    """Objects exposed here will be automatically available from the shell."""
    return dict(app=app, db=db, models=models, forms=forms)


def create_database():
    """ build database """
    def add_reseller_product(product, months, initprice, extprice, reseller):
        reseller_product = ResellerProduct(months=months, init_price=initprice, ext_price=extprice, product=product, reseller=reseller).save(False)
        product_key = f'{product.name} {months} Months'
        ninja_product = ninja.add_product(product_key=product_key, notes=reseller.name, cost=initprice)
        if ninja_product:
            reseller_product.ninja_product_id = ninja_product.id
            reseller_product.save(False)

    def add_phone(name, price):
        phone = Phone(name=name, price=price).save(False)
        product_key = f'Phone-{phone.name}'
        ninja_product = ninja.add_product(product_key=product_key, notes="Phone", cost=price)
        if ninja_product:
            phone.ninja_product_id = ninja_product.id
            phone.save(False)

    db.create_all()
    Phone(name='None', price=0.00).save(False)
    User(name='admin', password='admin', user_type=User.Type.super_admin, activated=User.Status.active).save(False)
    User(name='user', password='user', user_type=User.Type.user, activated=User.Status.active).save(False)
    reseller_nitrix = Reseller(name='NITRIX', comments='Main reseller').save(False)
    ninja_client = ninja.add_client(name=reseller_nitrix.name)
    if ninja_client:
        reseller_nitrix.ninja_client_id = ninja_client.id
    product_gold = Product(name='Gold').save(False)
    product_silver = Product(name='Silver').save(False)
    product_bronsa = Product(name='Bronsa').save(False)
    add_reseller_product(months=1, initprice=6.78, extprice=4.55, product=product_gold, reseller=reseller_nitrix)
    add_reseller_product(months=3, initprice=16.50, extprice=10.55, product=product_gold, reseller=reseller_nitrix)
    add_reseller_product(months=6, initprice=30.45, extprice=19.55, product=product_gold, reseller=reseller_nitrix)
    # add_reseller_product(months=12, price=50.0, product=product_gold, reseller=reseller_nitrix)
    # add_reseller_product(months=1, price=4.25, product=product_silver, reseller=reseller_nitrix)
    # add_reseller_product(months=3, price=11.50, product=product_silver, reseller=reseller_nitrix)
    # add_reseller_product(months=6, price=19.45, product=product_silver, reseller=reseller_nitrix)
    # add_reseller_product(months=12, price=35.99, product=product_silver, reseller=reseller_nitrix)
    # add_reseller_product(months=1, price=2.50, product=product_bronsa, reseller=reseller_nitrix)
    # add_reseller_product(months=3, price=6.99, product=product_bronsa, reseller=reseller_nitrix)
    # add_reseller_product(months=6, price=12.45, product=product_bronsa, reseller=reseller_nitrix)
    # add_reseller_product(months=12, price=20.99, product=product_bronsa, reseller=reseller_nitrix)
    add_phone(name="Samsung", price=54.00)
    add_phone(name="Nokia", price=38.00)
    add_phone(name="Lg", price=30.00)
    db.session.commit()


@app.cli.command()
def create_db():
    """Create the configured database."""
    create_database()


@app.cli.command()
@click.confirmation_option(prompt='Are you sure?')
def drop_db():
    """Drop the current database."""
    db.drop_all()


@app.cli.command()
@click.confirmation_option(prompt='Are you sure?')
def reset_db():
    """Reset the current database."""
    db.drop_all()
    create_database()


if __name__ == '__main__':
    app.run()
