from app.models import Product, Phone, Reseller, Account
from datetime import datetime


ALLOWED_PRODUCTS = [i.name for i in Product.query.all()]
ALLOWED_PHONES = [i.name for i in Phone.query.all()]
ALLOWED_RESELLERS = [i.name for i in Reseller.query.all()]


def name_in_db(field, value, error):
    if Account.query.filter(Account.name == value).first():
        error(field, f'Account for {value} is already created.')


def date_is_valid(field, value, error):
    try:
        past = datetime.strptime(value, "%Y-%m-%d")
        present = datetime.now()
        if past.date() > present.date():
            error(field, f'{past} can not be a date in future')
    except Exception:
        error(field, f'{value} is not valid date')


schema = {
    'name':   {'type': 'string', 'maxlength': 60, 'check_with': name_in_db, 'empty': False},
    'product':   {'type': 'string', 'allowed': ALLOWED_PRODUCTS, 'empty': False},
    'phone':   {'type': 'string', 'allowed': ALLOWED_PHONES, 'empty': False},
    'imei':   {'type': 'string', 'nullable': True, 'maxlength': 60},
    'resseler':   {'type': 'string', 'allowed': ALLOWED_RESELLERS, 'empty': False},
    'sim':   {'type': 'string', 'nullable': True, 'maxlength': 20},
    'activation_date':   {'type': 'string', 'nullable': False, 'check_with': date_is_valid},
    'months':   {'type': 'string', 'empty': False, 'allowed': [
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']},
    }
