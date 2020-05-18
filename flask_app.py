#!python
import click
from app import create_app, db, models, forms
from app.models import User, Account, Product, Reseller

app = create_app()


# flask cli context setup
@app.shell_context_processor
def get_context():
    """Objects exposed here will be automatically available from the shell."""
    return dict(app=app, db=db, models=models, forms=forms)


def create_database():
    """ build database """
    db.create_all()
    # add supper user acc
    for i in range(10):
        user = User(name='admin-{}'.format(i), password='admin', user_type='super_user', activated=True)
        user.save()
        product = Product(name='Kiev Star-{}'.format(i))
        product.save()
        reseller = Reseller(name='Dima-{}'.format(i), comments='Good reseller')
        reseller.save()
        acc = Account(name='Account A-{}'.format(i), sim='1234567890', comment='Comment', months=3)
        acc.product = product
        acc.reseller = reseller
        acc.save()


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
