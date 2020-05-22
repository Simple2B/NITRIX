from . import db


class ModelMixin(object):

    def save(self, non_commit=False):
        # Save this model to the database.
        db.session.add(self)
        if not non_commit:
            db.session.commit()
        return self


# Add your own utility classes and functions here.
