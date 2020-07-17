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


def organize_list_starting_with_value(input_list, value):
    try:
        default_phone_value_index = input_list.index([item for item in input_list if item.name == value][0])
    except ValueError:
        return input_list
    default_value = input_list.pop(default_phone_value_index)
    input_list.insert(0, default_value)
    return input_list
