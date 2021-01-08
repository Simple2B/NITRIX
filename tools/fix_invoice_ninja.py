import datetime
from app.models import Account, ResellerProduct
from app.ninja import NinjaInvoice
# from app.ninja import api
from app.logger import log
from app.utils import ninja_product_name



def restore_invoice_ninja_invoice_items():
    accounts = [i for i in Account.query.all() if not i.deleted]
    invoices = [dict(invoice=i, fixed=False) for i in NinjaInvoice.all() if not i.is_deleted]

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
                    for invoice_items in invoice.invoice_items:
                        if notes == invoice_item['notes'] and phone_name == invoice_item["product_key"]:
                            log(log.DEBUG, "Found phone item for [%s] in invoice [%s]", account.name, invoice.id)
                            break
                    else:
                        invoice.add_item(
                            phone_name,
                            notes,
                            cost=account.phone.price,
                        )

            # 3 get activation sim discount invoice item note
            pass
        # Account extensions
        # for extension in account.extensions:
        #     invoice_date = extension.extension_date.replace(day=1).strftime("%Y-%m-%d")
        #     inv = get_invoice(invoice_date, account.reseller.name)
        #     if not inv:
        #         log(log.ERROR, "Could not find invoice for acc [%s]. Extension", account.name)
        #     else:
        #         pass

        # for invoice in invoices:
        #     if (
        #         invoice.client_id == account.reseller.ninja_client_id
        #         and account_invoice_date == invoice.invoice_date
        #         and account_invoice_date > "2020-08-01"
        #     ):
        #         log(log.DEBUG, "Client id is [%s]", invoice.invoice_date)
        #         for items in invoice.invoice_items:
        #             pass
    pass
