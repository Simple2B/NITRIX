from datetime import timedelta, date
from sqlalchemy import and_
from app.models import (
    HistoryChange,
    Reseller,
    ResellerProduct,
    Account,
    AccountExtension,
    Phone,
)
from app.ninja import api as ninja
from app.ninja import NinjaInvoice
from app.utils import ninja_product_name
from app.logger import log
from config import SIM_COST_DISCOUNT, SIM_COST_ACCOUNT_COMMENT

ACCOUNT_CHANGES = [
    "name",
    "sim",
    "product",
    "phone",
    "reseller",
    "activation date",
    "months",
]

ZERO_PRICE = 0.0


def get_monday(day: date):
    """get date of monday on this week"""
    day_of_week = day.isocalendar()[2]
    delta = timedelta(days=(day_of_week - 1))
    return day - delta


def get_current_invoice(invoice_date: str, ninja_client_id: str) -> NinjaInvoice:
    log(log.DEBUG, "[SHED] Get all invoices...")
    invoices: list[NinjaInvoice] = [i for i in NinjaInvoice.all() if not i.is_deleted]
    log(log.DEBUG, "[SHED] Got [%s] invoices!", len(invoices))
    for invoice in invoices:
        if invoice.date == invoice_date and invoice.client_id == ninja_client_id:
            # found invoice

            log(log.DEBUG, " [SHED] add_ninja_invoice: found invoice [%s]", invoice.id)
            return invoice

    # need a new invoice
    log(log.DEBUG, "[SHED] add_ninja_invoice: need create new invoice!")
    return NinjaInvoice.add(ninja_client_id, invoice_date)


def creation_reseller_product(change: HistoryChange):
    assert change.change_type == HistoryChange.EditType.creation_reseller_product
    reseller_product: ResellerProduct = ResellerProduct.query.get(change.item_id)
    product_key = ninja_product_name(
        reseller_product.product.name, reseller_product.months
    )
    for prod in ninja.products:
        if (
            prod.product_key == product_key
            and prod.notes == reseller_product.reseller.name
        ):
            ninja_product = prod
            break
    else:
        ninja_product = ninja.add_product(
            product_key=product_key,
            notes=reseller_product.reseller.name,
            cost=reseller_product.init_price,
        )
    assert ninja_product
    reseller_product.ninja_product_id = ninja_product.id
    reseller_product.save()
    return True


def changes_reseller_product(change: HistoryChange):
    assert change.change_type == HistoryChange.EditType.changes_reseller_product
    if change.value_name not in ("months", "init_price"):
        log(
            log.INFO,
            "[SHED] reseller_prod[%d] change field [%s] ignored",
            change.item_id,
            change.value_name,
        )
        return True
    reseller_product: ResellerProduct = ResellerProduct.query.get(change.item_id)
    ninja_prod_id = reseller_product.ninja_product_id
    ninja_product = ninja.get_product(ninja_prod_id)
    product_key = ninja_product.product_key
    cost = ninja_product.cost
    if change.value_name == "months":
        product_key = ninja_product_name(
            reseller_product.product.name, int(change.after_value_str)
        )
    elif change.value_name == "init_price":
        cost = float(change.after_value_str)

    assert ninja_product
    res = ninja.update_product(
        ninja_product.id,
        product_key=product_key,
        notes=reseller_product.reseller.name,
        cost=cost,
    )
    if not res:
        log(log.ERROR, "[SHED] Failed Update Product [%s]", ninja_product.id)
        return False
    return True


def creation_reseller(change: HistoryChange):
    assert change.change_type == HistoryChange.EditType.creation_reseller
    reseller: Reseller = Reseller.query.get(change.item_id)
    assert reseller
    if reseller.deleted:
        log(
            log.INFO,
            "[creation_reseller] reseller [%d] is deleted, skipping",
            reseller.id,
        )
        return True
    for client in ninja.clients:
        if client.name == reseller.name:
            ninja_client = client
            break
    else:
        # create ninja client (Our reseller)
        ninja_client = ninja.add_client(name=reseller.name)
    assert ninja_client
    reseller.ninja_client_id = ninja_client.id
    reseller.save()
    return True


def changes_reseller(change: HistoryChange):
    assert change.change_type == HistoryChange.EditType.changes_reseller
    reseller: Reseller = Reseller.query.get(change.item_id)
    assert reseller
    if reseller.deleted:
        log(
            log.INFO,
            "[creation_reseller] reseller [%d] is deleted, skipping",
            reseller.id,
        )
        return True
    if change.value_name != "name":
        log(
            log.WARNING,
            "[SHED] Unexpected value (%s) in [%d]",
            change.value_name,
            change.item_id,
        )
        return True
    res = ninja.update_client(reseller.ninja_client_id, change.after_value_str)
    if not res:
        log(log.ERROR, "[SHED] Failed Update Client [%s]", reseller.ninja_client_id)
        return False
    return True


def extension_account_new(change: HistoryChange):
    assert change.change_type == HistoryChange.EditType.extension_account_new
    ext_account: AccountExtension = AccountExtension.query.get(change.item_id)
    account = ext_account.account
    invoice_date = get_monday(change.date).strftime("%Y-%m-%d")
    reseller_product: ResellerProduct = ResellerProduct.query.filter(
        and_(
            ResellerProduct.product_id == ext_account.product_id,
            ResellerProduct.reseller_id == ext_account.reseller_id,
            ResellerProduct.months == ext_account.months,
        )
    ).first()
    # if reseller have such product we set his cost else we set 0
    ext_price = reseller_product.ext_price if reseller_product else ZERO_PRICE
    current_invoice = get_current_invoice(
        invoice_date, account.reseller.ninja_client_id
    )
    assert current_invoice
    extension_date = ext_account.extension_date
    extension_month = ext_account.months
    mode = "Extended"
    added_item = current_invoice.add_item(
        ninja_product_name(account.product.name, extension_month),
        f'{account.name}.  {mode}: {extension_date.strftime("%Y-%m-%d")}',
        cost=ext_price,
    )
    assert added_item
    return True


def extensions_account_change(change: HistoryChange):
    assert change.change_type == HistoryChange.EditType.extensions_account_change
    ext_account: AccountExtension = AccountExtension.query.get(change.item_id)
    account: Account = ext_account.account
    if account.deleted:
        log(
            log.INFO,
            "[extensions_account_change] account [%d] is deleted, skipping",
            account.id,
        )
        return True
    invoice_date = get_monday(change.date).strftime("%Y-%m-%d")
    invoice: NinjaInvoice = get_current_invoice(
        invoice_date, account.reseller.ninja_client_id
    )
    assert invoice
    reseller_product: ResellerProduct = ResellerProduct.query.filter(
        and_(
            ResellerProduct.product_id == ext_account.product_id,
            ResellerProduct.reseller_id == ext_account.reseller_id,
            ResellerProduct.months == ext_account.months,
        )
    ).first()

    # if reseller have such product we set his cost else we set 0
    ext_price = reseller_product.ext_price if reseller_product else ZERO_PRICE

    for item in invoice.line_items:
        log(log.DEBUG, "[SHED] update invoice item [%s]", item.notes)
        if change.value_name == "extension_date":
            date = change.before_value_str
        else:
            date = ext_account.extension_date.strftime("%Y-%m-%d")
        notes = f"{account.name}.  Extended: {date}"
        log(log.DEBUG, "[SHED] new notes :[%s]", notes)
        if item.notes == notes:
            item.product_key = (
                ninja_product_name(account.product.name, ext_account.months),
            )
            item.notes = f'{account.name}.  Extended: {ext_account.extension_date.strftime("%Y-%m-%d")}'
            item.cost = ext_price

            invoice.save()
            break
    #####
    return True


def changes_account(change: HistoryChange):
    assert change.change_type == HistoryChange.EditType.changes_account
    # if change.value_name == "activation_date":
    #     account: Account = Account.query.get(change.item_id)
    #     if account.deleted:
    #         log(
    #             log.INFO,
    #             "[changes_account] account [%d] is deleted, skipping",
    #             account.id,
    #         )
    #         return True
    #     invoice_date = get_monday(change.date).strftime("%Y-%m-%d")
    #     invoice = get_current_invoice(invoice_date, account.reseller.ninja_client_id)
    #     if not invoice:
    #         log(
    #             log.WARNING,
    #             "[SHED] Cant find invoice in [%s] for [%s]",
    #             invoice_date,
    #             account.reseller.ninja_client_id,
    #         )
    #         return True
    #     date = account.activation_date.strftime("%Y-%m-%d")
    #     notes = f"{account.name}.  Activated: {change.before_value_str}"
    #     new_notes = f"{account.name}.  Activated: {date}"
    #     log(log.DEBUG, "[SHED] new notes :[%s]", new_notes)
    #     for item in invoice.line_items:
    #         log(log.DEBUG, "[SHED] update invoice item [%s]", item.notes)
    #         if item.notes == notes:
    #             # invoice.line_items.remove(item)
    #             # invoice.update_item(item, new_notes)
    #             log(log.DEBUG, "[SHED] updated invoice item [%s]", item.notes)
    #             item.notes = new_notes
    #             invoice.save()
    #             break
    return True


def creation_account(change: HistoryChange):
    assert change.change_type == HistoryChange.EditType.creation_account
    log(log.INFO, "[SHED] Change is [%s]", change)
    account: Account = Account.query.get(change.item_id)
    if account.deleted:
        log(
            log.INFO, "[creation_account] account [%d] is deleted, skipping", account.id
        )
        return True
    invoice_date = get_monday(change.date).strftime("%Y-%m-%d")
    reseller_product: ResellerProduct = ResellerProduct.query.filter(
        and_(
            ResellerProduct.product_id == account.product_id,
            ResellerProduct.reseller_id == account.reseller_id,
            ResellerProduct.months == account.months,
        )
    ).first()

    # if reseller have such product we set his cost else we set 0
    init_price = reseller_product.init_price if reseller_product else ZERO_PRICE

    current_invoice = get_current_invoice(
        invoice_date, account.reseller.ninja_client_id
    )
    assert current_invoice
    mode = "Activated"
    notes = f'{account.name}.  {mode}: {account.activation_date.strftime("%Y-%m-%d")}'
    added_item = current_invoice.add_item(
        ninja_product_name(account.product.name, account.months),
        notes,
        cost=init_price,
    )
    assert added_item, f"Could not add item [{notes}]"

    if account.phone.name != "None":
        phone_name = f"Phone-{account.phone.name}"
        notes = (
            f'{account.name}.  {mode}: {account.activation_date.strftime("%Y-%m-%d")}'
        )
        added_item = current_invoice.add_item(
            phone_name,
            notes,
            cost=account.phone.price,
        )
        assert added_item, f"Could not add item [{notes}]"

    if SIM_COST_ACCOUNT_COMMENT in account.comment:
        notes = "SIM Cost"
        added_item = current_invoice.add_item(
            notes,
            f'{account.name}.  {mode}: {account.activation_date.strftime("%Y-%m-%d")}',
            SIM_COST_DISCOUNT,
        )
        assert added_item, f"Could not add item [{notes}]"
    return True


def creation_phone(change: HistoryChange):
    assert change.change_type == HistoryChange.EditType.creation_phone
    phone: Phone = Phone.query.get(change.item_id)
    if phone.deleted:
        log(log.INFO, "[creation_phone] phone [%d] is deleted, skipping", phone.id)
        return True
    product_key = f"Phone-{phone.name}"
    ninja_product = ninja.add_product(
        product_key=product_key, notes="Phone", cost=phone.price
    )
    assert ninja_product
    phone.ninja_product_id = ninja_product.id
    phone.save()
    log(
        log.INFO,
        "[SHED] creation_phone [%s] created",
        ninja_product,
    )
    return True


def changes_phone(change: HistoryChange):
    assert change.change_type == HistoryChange.EditType.changes_phone
    phone: Phone = Phone.query.get(change.item_id)
    if phone.deleted:
        log(log.INFO, "[changes_phone] phone [%d] is deleted, skipping", phone.id)
        return True
    product_key = f"Phone-{phone.name}"
    ninja_product = ninja.get_product(phone.ninja_product_id)
    assert ninja_product
    ninja.update_product(
        ninja_product.id,
        product_key=product_key,
        notes="Phone",
        cost=phone.price,
    )
    log(
        log.INFO,
        "[SHED] changes_phone [%s] update_product",
        phone.id,
    )
    return True


def deletion_phone(change: HistoryChange):
    assert change.change_type == HistoryChange.EditType.deletion_phone
    phone: Phone = Phone.query.get(change.item_id)
    ninja_product = ninja.get_product(phone.ninja_product_id)
    assert ninja_product
    ninja.delete_product(ninja_product.id)
    log(
        log.INFO,
        "[SHED] ninja product [%s] deleted",
        ninja_product.product_key,
    )
    return True


def creation_product(change: HistoryChange):
    # creation product does not change InvoiceNinja
    return True
