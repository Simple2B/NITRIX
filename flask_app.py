#!python
import click
from app import create_app, db, models, forms
from app.models import User, Account, Product, Reseller, AccountExtension, ResellerProduct, Phone

app = create_app()


# flask cli context setup
@app.shell_context_processor
def get_context():
    """Objects exposed here will be automatically available from the shell."""
    return dict(app=app, db=db, models=models, forms=forms)


def create_database():
    """ build database """
    db.create_all()
    Phone(name='None').save(False)
    user = User(name='admin', password='admin', user_type=User.Type.super_admin, activated=User.Status.active)
    acc0 = Account(name='Account 0', sim='1234567890', comment='Comment', reseller_id=1, product_id=1, months=3)
    acc0.save(False)
    user.save(False)
    # add supper user acc
    for i in range(3):
        User(name='user-{}'.format(i), password='user', user_type=User.Type.user,
             activated=User.Status.active).save(False)
        User(name='admin-{}'.format(i),
             password='admin', user_type=User.Type.admin, activated=User.Status.active).save(False)
        product = Product(name='Kiev Star-{}'.format(i))
        product.save(False)
        reseller = Reseller(name='Dima-{}'.format(i), comments='Good reseller')
        reseller.save(False)
        acc = Account(name='Account A-{}'.format(i), sim='1234567890', comment='Comment', months=3)
        acc.product = product
        acc.reseller = reseller
        acc.save(False)

    product = Product(name='Product 1')
    product.save(False)
    product2 = Product(name='Product 2')
    product.save(False)
    reseller = Reseller(name='Reseller 1', comments='The best reseller')
    reseller.save(False)
    product1 = ResellerProduct(months = 1, price=16.78, product=product, reseller=reseller); product1.save(False)  # noqa
    product2 = ResellerProduct(months = 2, price=26.78, product=product2, reseller=reseller); product2.save(False)  # noqa
    product3 = ResellerProduct(months = 3, price=36.78, product=product, reseller=reseller); product3.save(False)  # noqa

    AccountExtension(account_id=acc0.id, reseller_id=1, months=2).save(False)
    AccountExtension(account_id=acc0.id, reseller_id=2, months=4).save(False)
    AccountExtension(account_id=acc0.id, reseller_id=3, months=7).save(False)
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
