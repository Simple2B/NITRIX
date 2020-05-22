#!python
import click
from app import create_app, db, models, forms
from app.models import User, Account, Product, Reseller, AccountExtension

app = create_app()


# flask cli context setup
@app.shell_context_processor
def get_context():
    """Objects exposed here will be automatically available from the shell."""
    return dict(app=app, db=db, models=models, forms=forms)


def create_database():
    """ build database """
    db.create_all()
    user = User(name='admin', password='admin', user_type=User.Type.super_admin, activated=User.Status.active)
    acc0 = Account(name='Account 0', sim='1234567890', comment='Comment', reseller_id=1, product_id=1, months=3)
    acc0.save()
    user.save(non_commit=True)
    # add supper user acc
    for i in range(10):
        User(name='user-{}'.format(i),
             password='user', user_type=User.Type.user, activated=User.Status.active).save(non_commit=True)
        User(name='admin-{}'.format(i),
             password='admin', user_type=User.Type.admin, activated=User.Status.active).save(non_commit=True)
        product = Product(name='Kiev Star-{}'.format(i))
        product.save(non_commit=True)
        reseller = Reseller(name='Dima-{}'.format(i), comments='Good reseller')
        reseller.save(non_commit=True)
        acc = Account(name='Account A-{}'.format(i), sim='1234567890', comment='Comment', months=3)
        acc.product = product
        acc.reseller = reseller
        acc.save(non_commit=True)
    AccountExtension(account_id=acc0.id, reseller_id=1, months=2).save(non_commit=True)
    AccountExtension(account_id=acc0.id, reseller_id=2, months=4).save(non_commit=True)
    AccountExtension(account_id=acc0.id, reseller_id=3, months=7).save(non_commit=True)
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
