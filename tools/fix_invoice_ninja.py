import datetime
from app.models import Account, ResellerProduct
from app.ninja import NinjaInvoice
# from app.ninja import api
from app.logger import log
from app.utils import ninja_product_name
from config import SIM_COST_DISCOUNT, SIM_COST_ACCOUNT_COMMENT


def restore_invoice_ninja_invoice_items():
    accounts = [i for i in Account.query.all() if not i.deleted]
    invoices = [dict(invoice=i, fixed=False) for i in NinjaInvoice.all() if not i.is_deleted]
    all_invoice_items = []
    for inv in invoices:
        invoice = inv["invoice"]
        all_invoice_items += [(i, invoice.id) for i in invoice.invoice_items]

    def find_invoice_item(notes, product_keys=None):
        for i in all_invoice_items:
            if product_keys is None:
                if i[0]['notes'] == notes:
                    return i[1]
            else:
                if i[0]['notes'] == notes and i[0]["product_key"] in product_keys:
                    return i[1]
        return None

    def get_invoice(invoice_date, client_id):
        for inv in invoices:
            invoice = inv["invoice"]
            if invoice.client_id == client_id and invoice.invoice_date == invoice_date:
                return inv
        return None

    for account in accounts:
        # Activation account
        if account.activation_date >= datetime.datetime(2020, 9, 1, 0, 0):
            invoice_date = account.activation_date.replace(day=1).strftime(
                "%Y-%m-%d"
            )
            inv = get_invoice(invoice_date, account.reseller.ninja_client_id)
            if not inv:
                log(log.ERROR, "Could not find invoice for acc [%s]. Activation", account.name)
            else:
                invoice = inv["invoice"]
                notes = f"{account.name}.  Activated: {account.activation_date.strftime('%Y-%m-%d')}"

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
                product_key = ninja_product_name(account.product.name, account.months)
                for invoice_item in invoice.invoice_items:
                    if notes == invoice_item['notes'] and product_key == invoice_item["product_key"]:
                        log(log.DEBUG, "Found activation for [%s] in invoice [%s]", account.name, invoice.id)
                        break
                    else:
                        extended_notes = f"{account.name}.  Extended: {account.activation_date.strftime('%Y-%m-%d')}"
                        if extended_notes == invoice_item['notes'] and product_key == invoice_item["product_key"]:
                            log(
                                    log.DEBUG,
                                    "Found extention as activation for [%s] in invoice [%s]",
                                    account.name,
                                    invoice.id
                                )
                            break
                else:
                    log(log.DEBUG, "RESTORE activation for [%s] in invoice [%s]", account.name, invoice.id)
                    invoice.add_item(
                        product_key,
                        notes,
                        cost=reseller_product.init_price if reseller_product else 0,
                    )
                    inv["fixed"] = True

                if account.phone.name != "None":
                    phone_name = f"Phone-{account.phone.name}"
                    for invoice_item in invoice.invoice_items:
                        if notes == invoice_item['notes'] and phone_name == invoice_item["product_key"]:
                            log(log.DEBUG, "Found phone item for [%s] in invoice [%s]", account.name, invoice.id)
                            break
                    else:
                        log(log.DEBUG, "Restore phone item  for [%s] in invoice [%s]", account.name, invoice.id)
                        invoice.add_item(
                            phone_name,
                            notes,
                            cost=account.phone.price,
                        )
                if SIM_COST_ACCOUNT_COMMENT in account.comment.strip():
                    sim_cost = 'SIM Cost'
                    for invoice_item in invoice.invoice_items:
                        if notes == invoice_item['notes'] and sim_cost == invoice_item["product_key"]:
                            log(log.DEBUG, "Found sim cost item for [%s] in invoice [%s]", account.name, invoice.id)
                            break
                    else:
                        log(log.DEBUG, "Restore sim cost item for [%s] in invoice [%s]", account.name, invoice.id)
                        invoice.add_item(
                            sim_cost,
                            notes,
                            cost=SIM_COST_DISCOUNT,
                        )
        #  Extensions
        for extension in account.extensions:
            extension_date = extension.extension_date
            if extension_date < datetime.datetime(2020, 9, 1, 0, 0):
                continue
            extension_month = extension.months
            invoice_date = extension_date.replace(day=1).strftime(
                "%Y-%m-%d"
            )
            inv = get_invoice(invoice_date, extension.reseller.ninja_client_id)
            if not inv:
                log(log.ERROR, "Could not find invoice for acc [%s]. Extended", account.name)
            else:
                invoice = inv["invoice"]
                notes = f"{account.name}.  Extended: {extension_date.strftime('%Y-%m-%d')}"
                reseller_product = (
                    ResellerProduct.query.filter(ResellerProduct.reseller_id == extension.reseller_id)
                    .filter(ResellerProduct.product_id == extension.product_id)
                    .filter(ResellerProduct.months == extension_month)
                    .first()
                )
                if not reseller_product:
                    # Locking for this product in NITRIX reseller
                    reseller_product = (
                        ResellerProduct.query.filter(ResellerProduct.reseller_id == 1)
                        .filter(ResellerProduct.product_id == extension.product_id)
                        .filter(ResellerProduct.months == extension_month)
                        .first()
                    )
                # product_key_a = ninja_product_name(account.product.name, extension_month)
                product_key_e = ninja_product_name(extension.product.name, extension_month)
                # invoice_id = find_invoice_item(notes, [product_key_a, product_key_e])
                invoice_id = find_invoice_item(notes)
                if invoice_id:
                    log(log.DEBUG, "Found extension for [%s] in invoice [%s]", account.name, invoice_id)
                else:
                    log(log.DEBUG, "RESTORE extension for [%s] in invoice [%s]", account.name, invoice.id)
                    invoice.add_item(
                        product_key_e,
                        notes,
                        cost=reseller_product.ext_price if reseller_product else 0,
                    )
    pass
