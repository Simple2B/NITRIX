import csv
from io import TextIOWrapper
from datetime import datetime

from cerberus import Validator
from flask import flash, session

from config import SIM_COST_DISCOUNT, SIM_COST_ACCOUNT_COMMENT
from app.database import db
from app.logger import log
from app.models import (
    Account,
    Product,
    Reseller,
    AccountExtension,
    AccountChanges,
    Phone,
    ResellerProduct,
)
from app.ninja import NinjaInvoice
from app.utils import ninja_product_name, organize_list_starting_with_value
from app.ninja import api as ninja


def all_phones():
    phones = Phone.query.filter(
        Phone.deleted == False, Phone.status == Phone.Status.active  # noqa E712
    ).order_by(
        Phone.name
    )  # noqa E712
    all_phones = phones.all()
    all_phones = organize_list_starting_with_value(all_phones, "None")
    return all_phones


class AccountDelete():
    def __init__(self, id):
        self.id = id

    def delete_account(self):
        if not self.id:
            flash("Wrong request", "danger")
            return False
        account_id = int(self.id)
        account = Account.query.filter(Account.id == account_id).first()
        change = AccountChanges(account=account)
        change.user_id = session.get("_user_id")
        change.change_type = AccountChanges.ChangeType.deleted
        change.new_value_str = "None"
        change.value_str = "Deleted"
        change.save()
        account.delete()
        flash('Account successfully deleted.', 'success')
        return True


class CsvValidator():
    def __init__(self, file_object):
        ALLOWED_PRODUCTS = [i.name for i in Product.query.all()]
        ALLOWED_PHONES = [i.name for i in Phone.query.all()]
        ALLOWED_RESELLERS = [i.name for i in Reseller.query.all()]
        SCHEMA = {
            "name": {
                "type": "string",
                "maxlength": 60,
                "check_with": self.name_in_db,
                "empty": False,
            },
            "product": {"type": "string", "allowed": ALLOWED_PRODUCTS, "empty": False},
            "phone": {"type": "string", "allowed": ALLOWED_PHONES, "empty": False},
            "imei": {"type": "string", "nullable": True, "maxlength": 60},
            "reseller": {"type": "string", "allowed": ALLOWED_RESELLERS, "empty": False},
            "sim": {"type": "string", "nullable": True, "maxlength": 20},
            "activation_date": {
                "type": "string",
                "nullable": False,
                "check_with": self.date_is_valid,
            },
            "months": {
                "type": "string",
                "empty": False,
                "allowed": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
            },
            "comment": {"type": "string", "nullable": True, "maxlength": 200},
            "sim_cost": {"type": "string", "empty": True}
        }
        self.v = Validator(SCHEMA)
        self.csv_file = file_object

    def name_in_db(self, field, value, error):
        if Account.query.filter(Account.name == value).first():
            error(field, f"Account for {value} is already created.")

    def date_is_valid(self, field, value, error):
        try:
            past = datetime.strptime(value, "%Y-%m-%d")
            present = datetime.now()
            if past.date() > present.date():
                error(field, f"{past} can not be a date in future")
        except ValueError:
            error(field, f"{value} is not valid date")

    def verify_file_integrity(self):
        if not self.csv_file.filename or not self.csv_file:
            log(log.WARNING, "File import failed: Either file is not in 'request.files' or filename is empty")
            flash("Could not import file without name. Check if your file is formatted properly and try again.",
                  'danger')
            return False
        return True

    def import_data_from_file(self):
        with TextIOWrapper(self.csv_file, encoding="utf-8") as _file:
            csv_reader = csv.DictReader(_file, delimiter=",")
            for i, row in enumerate(csv_reader):
                if not self.v.validate(row):
                    flash(
                        f'Could not validate row {i+1}. Please check imported data and try again. {self.v.errors}',
                        'danger')
                    log(log.WARNING, "Row validation error: %s", self.v.errors)
                    return False
                imported_account = Account(
                    name=row['name'],
                    product_id=Product.query.filter(Product.name == row['product']).first().id,
                    phone_id=Phone.query.filter(Phone.name == row['phone']).first().id,
                    imei=row['imei'],
                    reseller_id=Reseller.query.filter(Reseller.name == row['reseller']).first().id,
                    sim=row['sim'],
                    activation_date=datetime.strptime(row['activation_date'], "%Y-%m-%d"),
                    months=int(row['months']),
                    comment=row['comment'] if not row['sim_cost'] else row['comment'] +
                        f"\r\n\r\n{SIM_COST_ACCOUNT_COMMENT}"
                )
                db.session.add(imported_account)
        db.session.commit()
        log(log.INFO, "Import successfull")
        flash("Accounts are successfully imported", 'info')
        return True
