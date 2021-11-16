import csv
from io import TextIOWrapper
from datetime import datetime
from flask import flash, url_for
from flask import current_app as app
from cerberus import Validator

from config import SIM_COST_ACCOUNT_COMMENT
from app.models import (
    Account,
    Product,
    Reseller,
    AccountExtension,
    Phone,
    HistoryChange,
)
from app.forms import AccountForm
from app.database import db
from app.logger import log

from app.utils import organize_list_starting_with_value


EXTENDED = "Extended"


def all_phones():
    phones = Phone.query.filter(
        Phone.deleted == False, Phone.status == Phone.Status.active  # noqa E712
    ).order_by(
        Phone.name
    )  # noqa E712
    all_phones = phones.all()
    all_phones = organize_list_starting_with_value(all_phones, "None")
    return all_phones


def document_changes_if_exist(account, form):
    if account.name != form.name.data:
        # Changed account name
        HistoryChange(
            change_type=HistoryChange.EditType.changes_account,
            item_id=account.id,
            value_name="name",
            before_value_str=account.name,
            after_value_str=form.name.data,
        ).save()
        flash(f"In account {account.name} name changed to {form.name.data}", "info")
    if account.sim != form.sim.data:
        # Changed account SIM
        HistoryChange(
            change_type=HistoryChange.EditType.changes_account,
            item_id=account.id,
            value_name="sim",
            before_value_str=account.sim if account.sim else "[Empty]",
            after_value_str=form.sim.data,
        ).save()
        flash(f"In account {account.name} sim changed to {form.sim.data}", "info")
    if account.product_id != form.product_id.data:
        # Changed account product
        new_product = Product.query.get(form.product_id.data).name
        old_product = Product.query.get(account.product_id).name
        HistoryChange(
            change_type=HistoryChange.EditType.changes_account,
            item_id=account.id,
            value_name="product",
            before_value_str=old_product,
            after_value_str=new_product,
        ).save()
        flash(f"In account {account.name} product changed to {new_product}", "info")
    if account.phone_id != form.phone_id.data:
        # Changed account phone
        new_phone = Phone.query.get(form.phone_id.data).name
        HistoryChange(
            change_type=HistoryChange.EditType.changes_account,
            item_id=account.id,
            value_name="phone",
            before_value_str=(account.phone.name if account.phone.name else "[Empty]"),
            after_value_str=new_phone,
        ).save()
        flash(f"In account {account.name} phone changed to {new_phone}", "info")
    if account.reseller_id != form.reseller_id.data:
        # Changed account reseller
        new_reseller = Reseller.query.get(form.reseller_id.data).name
        HistoryChange(
            change_type=HistoryChange.EditType.changes_account,
            item_id=account.id,
            value_name="reseller",
            before_value_str=account.reseller.name,
            after_value_str=new_reseller,
        ).save()
        flash(f"In account {account.name} reseller changed to {new_reseller}", "info")
    if account.activation_date.strftime(
        "%Y-%m-%d"
    ) != form.activation_date.data.strftime("%Y-%m-%d"):
        # Changed account activation date
        HistoryChange(
            change_type=HistoryChange.EditType.changes_account,
            item_id=account.id,
            value_name="activation_date",
            before_value_str=account.activation_date.strftime("%Y-%m-%d"),
            after_value_str=form.activation_date.data.strftime("%Y-%m-%d"),
        ).save()
        flash(
            f'In account {account.name} activation date changed to {form.activation_date.data.strftime("%Y-%m-%d")}',
            "info",
        )

    if account.months != form.months.data:
        # Changed account months
        HistoryChange(
            change_type=HistoryChange.EditType.changes_account,
            item_id=account.id,
            value_name="months",
            before_value_str=str(account.months),
            after_value_str=str(form.months.data),
        ).save()
        flash(f"In account {account.name} months changed to {form.months.data}", "info")

    form = AccountForm(
        id=account.id,
        name=account.name,
        product_id=account.product_id,
        phone_id=account.phone_id,
        reseller_id=account.reseller_id,
        sim=account.sim,
        imei=account.imei,
        comment=account.comment,
        activation_date=account.activation_date,
        months=account.months,
    )
    form.products = Product.query.filter(Product.deleted == False)  # noqa E712
    form.resellers = Reseller.query.filter(Reseller.deleted == False)  # noqa E712
    form.phones = all_phones()
    form.extensions = AccountExtension.query.filter(
        AccountExtension.account_id == form.id.data
    ).all()
    form.name_changes = (
        HistoryChange.query.filter(HistoryChange.item_id == form.id.data)
        .filter(HistoryChange.change_type == HistoryChange.EditType.changes_account)
        .filter(HistoryChange.value_name == "name")
        .all()
    )
    form.sim_changes = (
        HistoryChange.query.filter(HistoryChange.item_id == form.id.data)
        .filter(HistoryChange.value_name == "sim")
        .all()
    )
    form.is_edit = True
    form.save_route = url_for("account.save")
    form.delete_route = url_for("account.delete")
    form.close_button = url_for("main.accounts")
    form.reseller_name = account.reseller.name
    form.history = HistoryChange.get_history(account)
    return form


class AccountController(object):
    def __init__(self, account_id=None, file_object=None):
        if account_id is not None:
            account_id = int(account_id)
            self.account = Account.query.filter(Account.id == account_id).first()
        else:
            self.account = None
        if self.account:
            self.new_account = False
        else:
            self.new_account = True
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
            "reseller": {
                "type": "string",
                "allowed": ALLOWED_RESELLERS,
                "empty": False,
            },
            "sim": {"type": "string", "nullable": True, "maxlength": 20},
            "activation_date": {
                "type": "string",
                "nullable": False,
                "check_with": self.date_is_valid,
            },
            "months": {
                "type": "string",
                "empty": False,
                "allowed": [
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "10",
                    "11",
                    "12",
                ],
            },
            "comment": {"type": "string", "nullable": True, "maxlength": 200},
            "sim_cost": {"type": "string", "empty": True},
        }
        self.v = Validator(SCHEMA)
        self.csv_file = file_object

    def account_form_edit(self):
        form = AccountForm(
            id=self.account.id,
            name=self.account.name,
            product_id=self.account.product_id,
            phone_id=self.account.phone_id,
            reseller_id=self.account.reseller_id,
            sim=self.account.sim,
            imei=self.account.imei,
            comment=self.account.comment,
            activation_date=self.account.activation_date,
            months=self.account.months,
        )
        form.products = Product.query.filter(Product.deleted == False)  # noqa E712
        form.resellers = Reseller.query.filter(Reseller.deleted == False)  # noqa E712
        form.phones = all_phones()
        form.extensions = AccountExtension.query.filter(
            AccountExtension.account_id == form.id.data
        ).all()
        form.name_changes = (
            HistoryChange.query.filter(HistoryChange.item_id == form.id.data)
            .filter(HistoryChange.change_type == HistoryChange.EditType.changes_account)
            .filter(HistoryChange.value_name == "name")
            .all()
        )
        form.sim_changes = (
            HistoryChange.query.filter(HistoryChange.item_id == form.id.data)
            .filter(HistoryChange.value_name == "sim")
            .all()
        )
        form.is_edit = True
        form.save_route = url_for("account.save")
        form.delete_route = url_for("account.delete")
        form.close_button = url_for("main.accounts")
        form.reseller_name = self.account.reseller.name
        form.history = HistoryChange.get_history(self.account)
        return form

    def account_form_new(
        self,
        prev_product=None,
        prev_reseller=None,
        prev_phone=None,
        prev_month=None,
        prev_simcost="yes",
    ):
        form = AccountForm()
        form.products = (
            organize_list_starting_with_value(
                Product.query.filter(Product.deleted == False)  # noqa E712
                .order_by(Product.name)
                .all(),
                prev_product,
            )
            if prev_product
            else Product.query.all()
        )
        if prev_simcost:
            form.sim_cost.default = prev_simcost
            form.process()
        form.month = prev_month
        form.resellers = organize_list_starting_with_value(
            Reseller.query.order_by(Reseller.name).all(),
            prev_reseller if prev_reseller else "NITRIX",
        )
        form.phones = (
            organize_list_starting_with_value(
                Phone.query.filter(Phone.deleted == False)  # noqa E712
                .order_by(Phone.name)
                .all(),
                prev_phone,
            )
            if prev_phone
            else Phone.query.all()
        )
        form.is_edit = False
        form.save_route = url_for("account.save")
        form.delete_route = url_for("account.delete")
        form.close_button = url_for("main.accounts")
        return form

    def save(self, form):
        log(log.INFO, "/account_save")
        form.name.data = form.name.data.strip()
        form.sim.data = form.sim.data.strip()
        form.comment.data = form.comment.data.strip()
        self.new_account = False
        if self.account:
            document_changes_if_exist(self.account, form)
            self.account.product_id = form.product_id.data
            self.account.reseller_id = form.reseller_id.data
            self.account.phone_id = form.phone_id.data
            self.account.sim = form.sim.data
            self.account.imei = form.imei.data
            self.account.comment = form.comment.data
            self.account.months = form.months.data
            self.account.name = form.name.data
            if self.account.activation_date.date() != form.activation_date.data:

                self.account.activation_date = form.activation_date.data

        else:
            if Account.query.filter(
                Account.name == form.name.data,
                Account.product_id == form.product_id.data,
            ).first():
                log(
                    log.WARNING, "Attempt to register account with existing credentials"
                )
                flash("Such account already exists", "danger")
                return False
            self.new_account = True
            if form.sim_cost.data == "yes":
                form.comment.data += f"\r\n\r\n{SIM_COST_ACCOUNT_COMMENT}"
            self.account = Account(
                name=form.name.data,
                product_id=form.product_id.data,
                reseller_id=form.reseller_id.data,
                phone_id=form.phone_id.data,
                sim=form.sim.data,
                imei=form.imei.data,
                comment=form.comment.data,
                activation_date=form.activation_date.data,
                months=form.months.data,
            )
            flash(f"Account {self.account.name} added", "info")
            log(log.INFO, "Created account: [%s]", self.account.name)
        if not 0 < self.account.months <= 12:
            flash("Months must be in 1-12", "danger")
            return False
        self.account.save()
        if self.new_account:
            HistoryChange(
                change_type=HistoryChange.EditType.creation_account,
                item_id=self.account.id,
            ).save()
        reseller = Reseller.query.filter(
            Reseller.id == self.account.reseller_id
        ).first()
        reseller.last_activity = datetime.now()
        reseller.save()
        log(log.INFO, "Account data was saved")
        return self.account

    def delete(self):
        log(log.INFO, "/account_delete")
        if not self.account:
            flash("Wrong request", "danger")
            return False
        HistoryChange(
            change_type=HistoryChange.EditType.deletion_account,
            item_id=self.account.id,
        ).save()

        self.account.name = f"{self.account.name}-Deleted-{datetime.now()}"
        self.account.deleted = True
        self.account.save()
        flash("Account successfully deleted.", "success")
        return True

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
            log(
                log.WARNING,
                "File import failed: Either file is not in 'request.files' or filename is empty",
            )
            flash(
                "Could not import file without name. Check if your file is formatted properly and try again.",
                "danger",
            )
            return False
        return True

    def import_data_from_file(self):
        with TextIOWrapper(self.csv_file, encoding="utf-8") as _file:
            csv_reader = csv.DictReader(_file, delimiter=",")
            for i, row in enumerate(csv_reader):
                if not self.v.validate(row):
                    flash(
                        f"Could not validate row {i+1}. Please check imported data and try again. {self.v.errors}",
                        "danger",
                    )
                    log(log.WARNING, "Row validation error: %s", self.v.errors)
                    return False
                imported_account = Account(
                    name=row["name"],
                    product_id=Product.query.filter(Product.name == row["product"])
                    .first()
                    .id,
                    phone_id=Phone.query.filter(Phone.name == row["phone"]).first().id,
                    imei=row["imei"],
                    reseller_id=Reseller.query.filter(Reseller.name == row["reseller"])
                    .first()
                    .id,
                    sim=row["sim"],
                    activation_date=datetime.strptime(
                        row["activation_date"], "%Y-%m-%d"
                    ),
                    months=int(row["months"]),
                    comment=row["comment"]
                    if not row["sim_cost"]
                    else row["comment"] + f"\r\n\r\n{SIM_COST_ACCOUNT_COMMENT}",
                )
                db.session.add(imported_account)
        db.session.commit()
        log(log.INFO, "Import successfull")
        if not app.config["TESTING"]:
            flash("Accounts are successfully imported", "info")
        return True
