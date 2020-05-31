from . import db


class ModelMixin(object):

    def save(self, commit=True):
        """ Save this model to the database. """
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """ Delete instance """
        db.session.delete(self)
        if commit:
            db.session.commit()
        return self


def ninja_product_name(product_name: str, months: int):
    return f'{product_name} {months} Months'
