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


@app.cli.command()
def create_db():
    """Create the configured database."""
    db.create_all()
    # add supper user acc
    user = User(name='admin', password='admin', user_type='super_user', activated=True)
    user.save()
    product = Product(name='Kiev Star', status=True)
    product.save()
    reseller = Reseller(name='Dima', status=True, comments='Good reseller')
    reseller.save()
    acc = Account(name='Account A', sim='1234567890', comment='Comment', months=3)
    acc.product = product
    acc.reseller = reseller
    acc.save()


@app.cli.command()
@click.confirmation_option(prompt='Drop all database tables?')
def drop_db():
    """Drop the current database."""
    db.drop_all()


if __name__ == '__main__':
    app.run()
