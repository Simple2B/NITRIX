import csv
from io import TextIOWrapper
from datetime import datetime
from flask import request, flash, url_for, session
from flask import current_app as app
from flask_login import current_user
from cerberus import Validator

from config import SIM_COST_DISCOUNT, SIM_COST_ACCOUNT_COMMENT
from app.models import (
    Account,
    Product,
    Reseller,
    AccountExtension,
    AccountChanges,
    Phone,
    ResellerProduct,
)
from app.forms import AccountForm
from app.database import db
from app.logger import log
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


def add_ninja_invoice(account: Account, is_new: bool, mode: str):
    reseller_product = (
        ResellerProduct.query.filter(ResellerProduct.reseller_id == account.reseller_id)
        .filter(ResellerProduct.product_id == account.product_id)
        .filter(ResellerProduct.months == account.months)
        .first()
    )
    if not reseller_product:
        # Locking for this product in NITRIX reseller
        reseller_product = (
            ResellerProduct.query.filter(ResellerProduct.reseller_id == 1)
            .filter(ResellerProduct.product_id == account.product_id)
            .filter(ResellerProduct.months == account.months)
            .first()
        )
    # invoice_date = datetime.now()
    # if account.activation_date > invoice_date:
    #     invoice_date = invoice_date.date().replace(day=1).strftime("%Y-%m-%d")
    # else:
    invoice_date = (
            account.activation_date.replace(day=1).strftime("%Y-%m-%d")
        )
    current_invoice = None
    invoices = [i for i in NinjaInvoice.all() if not i.is_deleted]
    for invoice in invoices:
        if (
            invoice.invoice_date == invoice_date
            and invoice.client_id == account.reseller.ninja_client_id
        ):
            # found invoice
            current_invoice = invoice
            break
    else:
        # need a new invoice
        current_invoice = NinjaInvoice.add(
            account.reseller.ninja_client_id, invoice_date
        )
    if current_invoice:
        added_item = current_invoice.add_item(
            ninja_product_name(account.product.name, account.months),
            f'{account.name}.  {mode}: {account.activation_date.strftime("%Y-%m-%d")}',
            cost=reseller_product.init_price if reseller_product else 0,
        )
        if not added_item:
            log(log.ERROR, "Could not add item to invoice in invoice Ninja!")
            return None
        if is_new:
            if account.phone.name != "None":
                phone_name = f"Phone-{account.phone.name}"
                added_item = current_invoice.add_item(
                    phone_name,
                    f'{account.name}.  {mode}: {account.activation_date.strftime("%Y-%m-%d")}',
                    cost=account.phone.price,
                )
                if not added_item:
                    log(log.ERROR, "Could not add item to invoice in invoice Ninja!")
                    return None
            if SIM_COST_ACCOUNT_COMMENT in account.comment:
                added_item = current_invoice.add_item(
                    "SIM Cost",
                    f'{account.name}.  {mode}: {account.activation_date.strftime("%Y-%m-%d")}',
                    SIM_COST_DISCOUNT,
                )
                if not added_item:
                    log(log.ERROR, "Could not add item to invoice in invoice Ninja!")
                    return None
        log(log.INFO, "Invoice into Invoice Ninja added successfully")
        return True
    else:
        log(log.ERROR, "Could not add invoice to Invoice Ninja!")
        return None


def document_changes_if_exist(account, form):
    if account.name != form.name.data:
        # Changed account name
        change = AccountChanges(account=account)
        change.user_id = session.get("_user_id")
        change.change_type = AccountChanges.ChangeType.name
        change.value_str = account.name
        change.new_value_str = form.name.data
        change.save()
        flash(f"In account {account.name} name changed to {form.name.data}", "info")
    if account.sim != form.sim.data:
        # Changed account SIM
        change = AccountChanges(account=account)
        change.user_id = session.get("_user_id")
        change.change_type = AccountChanges.ChangeType.sim
        change.new_value_str = form.sim.data
        change.value_str = account.sim if account.sim else "Empty"
        change.save()
        flash(f"In account {account.name} sim changed to {form.sim.data}", "info")
    if account.product_id != form.product_id.data:
        # Changed account product
        new_product = Product.query.get(form.product_id.data).name
        change = AccountChanges(account=account)
        change.user_id = session.get("_user_id")
        change.change_type = AccountChanges.ChangeType.product
        change.new_value_str = new_product
        change.value_str = account.product.name
        change.save()
        flash(f"In account {account.name} product changed to {new_product}", "info")
    if account.phone_id != form.phone_id.data:
        # Changed account phone
        new_phone = Phone.query.get(form.phone_id.data).name
        change = AccountChanges(account=account)
        change.user_id = session.get("_user_id")
        change.change_type = AccountChanges.ChangeType.phone
        change.new_value_str = new_phone
        change.value_str = account.phone.name if account.phone.name else "Empty"
        change.save()
        flash(f"In account {account.name} phone changed to {new_phone}", "info")
    if account.reseller_id != form.reseller_id.data:
        # Changed account reseller
        new_reseller = Reseller.query.get(form.reseller_id.data).name
        change = AccountChanges(account=account)
        change.user_id = session.get("_user_id")
        change.change_type = AccountChanges.ChangeType.reseller
        change.new_value_str = new_reseller
        change.value_str = account.reseller.name
        change.save()
        flash(f"In account {account.name} reseller changed to {new_reseller}", "info")
    if account.activation_date.strftime(
        "%Y-%m-%d"
    ) != form.activation_date.data.strftime("%Y-%m-%d"):
        # Changed account activation date
        change = AccountChanges(account=account)
        change.user_id = session.get("_user_id")
        change.change_type = AccountChanges.ChangeType.activation_date
        change.new_value_str = form.activation_date.data.strftime("%Y-%m-%d")
        change.value_str = account.activation_date.strftime("%Y-%m-%d")
        change.save()
        flash(
            f'In account {account.name} activation date changed to {form.activation_date.data.strftime("%Y-%m-%d")}',
            "info",
        )

    if account.months != form.months.data:
        # Changed account months
        change = AccountChanges(account=account)
        change.user_id = session.get("_user_id")
        change.change_type = AccountChanges.ChangeType.months
        change.new_value_str = form.months
        change.value_str = account.months
        change.save()
        flash(f"In account {account.name} months changed to {form.months}", "info")

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
            AccountChanges.query.filter(AccountChanges.account_id == form.id.data)
            .filter(AccountChanges.change_type == AccountChanges.ChangeType.name)
            .all()
        )
        form.sim_changes = (
            AccountChanges.query.filter(AccountChanges.account_id == form.id.data)
            .filter(AccountChanges.change_type == AccountChanges.ChangeType.sim)
            .all()
        )
        form.is_edit = True
        form.save_route = url_for("account.save")
        form.delete_route = url_for("account.delete")
        form.close_button = url_for("main.accounts")
        form.reseller_name = account.reseller.name
        form.history = AccountChanges.get_history(account)
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
            AccountChanges.query.filter(AccountChanges.account_id == form.id.data)
            .filter(AccountChanges.change_type == AccountChanges.ChangeType.name)
            .all()
        )
        form.sim_changes = (
            AccountChanges.query.filter(AccountChanges.account_id == form.id.data)
            .filter(AccountChanges.change_type == AccountChanges.ChangeType.sim)
            .all()
        )
        form.is_edit = True
        form.save_route = url_for("account.save")
        form.delete_route = url_for("account.delete")
        form.close_button = url_for("main.accounts")
        form.reseller_name = self.account.reseller.name
        form.history = AccountChanges.get_history(self.account)
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
        new_invoice = False
        if self.account:
            document_changes_if_exist(self.account, form)
            if self.account.activation_date != form.activation_date.data:
                new_invoice_date = form.activation_date.data.replace(day=1).strftime(
                    "%Y-%m-%d"
                )
                invoice_date = self.account.activation_date.replace(day=1).strftime(
                    "%Y-%m-%d"
                )
                invoices = [i for i in NinjaInvoice.all() if not i.is_deleted]

                if new_invoice_date != invoice_date:
                    new_invoice = True
                for invoice in invoices:
                    if (
                        invoice.invoice_date == invoice_date
                        and invoice.client_id == self.account.reseller.ninja_client_id
                    ):
                        # found invoice
                        for item in invoice.invoice_items:
                            log(log.DEBUG, item["notes"])
                            log(
                                log.DEBUG,
                                f"{self.account.name}.  "
                                f'Activated: {self.account.activation_date.strftime("%Y-%m-%d")}',
                            )
                            if item["notes"] == (
                                f"{self.account.name}.  "
                                f'Activated: {self.account.activation_date.strftime("%Y-%m-%d")}'
                            ):
                                invoice.delete_item(item)
                                invoice.save()
                                break
                        break
            self.account.name = form.name.data
            self.account.activation_date = form.activation_date.data
            self.account.product_id = form.product_id.data
            self.account.reseller_id = form.reseller_id.data
            self.account.phone_id = form.phone_id.data
            self.account.sim = form.sim.data
            self.account.imei = form.imei.data
            self.account.comment = form.comment.data
            self.account.months = form.months.data
            add_ninja_invoice(self.account, True, "Activated")

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
        if not 0 < self.account.months <= 12:
            flash("Months must be in 1-12", "danger")
            return False
        self.account.save()
        if self.new_account:
            change = AccountChanges(account=self.account)
            change.user_id = session.get("_user_id")
            change.change_type = AccountChanges.ChangeType.created
            change.new_value_str = "Created"
            change.value_str = "None"
            change.save()
            self.connect_to_ninja(self.account)
        reseller = Reseller.query.filter(
            Reseller.id == self.account.reseller_id
        ).first()
        reseller.last_activity = datetime.now()
        reseller.save()
        log(log.INFO, "Account data was saved")
        return self.account

    def connect_to_ninja(self, account):
        if ninja.configured:
            nina_api_result = add_ninja_invoice(account, self.new_account, "Activated")
            if not nina_api_result:
                log(
                    log.ERROR,
                    "Could not register account as invoice in Invoice Ninja!",
                )
                flash("WARNING! Account registration in Ninja failed!", "danger")

    def delete(self):
        log(log.INFO, "/account_delete")
        if not self.account:
            flash("Wrong request", "danger")
            return False
        change = AccountChanges(account=self.account)
        change.user_id = current_user.id
        change.change_type = AccountChanges.ChangeType.deleted
        change.new_value_str = "None"
        change.value_str = "Deleted"
        change.save()
        self.account.delete()
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
                self.connect_to_ninja(imported_account)
        db.session.commit()
        log(log.INFO, "Import successfull")
        if not app.config["TESTING"]:
            flash("Accounts are successfully imported", "info")
        return True
