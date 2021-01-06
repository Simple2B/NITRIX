from app.models.account import Account
from app.ninja import NinjaInvoice
# from app.ninja import api
from app.logger import log


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
        invoice_date = account.activation_date.replace(day=1).strftime(
            "%Y-%m-%d"
        )
        inv = get_invoice(invoice_date, account.reseller.ninja_client_id)
        if not inv:
            log(log.ERROR, "Could not find invoice for acc [%s]. Activation", account.name)
        else:
            invoice = inv["invoice"]
            activation_exists = False
            for invoice_items in invoice.invoice_items:
                if account.name in invoice_items['notes']:
                    activation_exists = True
                    log(log.DEBUG, "Found activation for [%s] in invoice [%s]", account.name, invoice.id)
                if account.name in invoice_items['notes']:
                    pass
            if not activation_exists:
                log(log.DEBUG, "No activation for [%s] in invoice [%s]", account.name, invoice.id)
                pass

            # 1 get activation invoice item note
            # 2 get activation sim discount invoice item note
            # 3 get activation phone invoice item note
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
