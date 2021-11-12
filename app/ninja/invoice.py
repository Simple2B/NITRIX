from datetime import datetime, date
from typing import Any
from pydantic import BaseModel
from app.logger import log
from app.ninja import api, ArrayData


class NinjaInvitations(BaseModel):
    id: str
    client_contact_id: str
    key: str
    link: str
    sent_date: str
    viewed_date: str
    opened_date: str
    updated_at: datetime
    archived_at: datetime


class NinjaInvoiceItem(BaseModel):
    {'product_key': 'Kryptr', 'notes': '5 Months', 'cost': 1000, 'product_cost': 0, 'quantity': 1, 'tax_name1': '', 'tax_rate1': 0, 'tax_name2': '', 'tax_rate2': 0, 'tax_name3': '', 'tax_rate3': 0, 'custom_value1': '', 'custom_value2': '', 'custom_value3': '', ...}


class _NinjaInvoice(BaseModel):
    id: str
    user_id: str
    project_id: str
    assigned_user_id: str
    amount: int
    balance: float
    client_id: str
    vendor_id: str
    status_id: int
    design_id: str
    recurring_id: str
    created_at: datetime
    updated_at: datetime
    archived_at: datetime
    is_deleted: bool
    number: str
    discount: float
    po_number: str
    date: str
    last_sent_date: str
    next_send_date: str
    due_date: date
    terms: str
    public_notes: str
    private_notes: str
    uses_inclusive_taxes: bool
    tax_name1: str
    tax_rate1: float
    tax_name2: str
    tax_rate2: float
    tax_name3: str
    tax_rate3: float
    total_taxes: float
    is_amount_discount: bool
    footer: str
    partial: float
    partial_due_date: str
    custom_value1: str
    custom_value2: str
    custom_value3: str
    custom_value4: str
    has_tasks: bool
    has_expenses: bool
    custom_surcharge1: float
    custom_surcharge2: float
    custom_surcharge3: float
    custom_surcharge4: float
    exchange_rate: float  # int
    custom_surcharge_tax1: bool
    custom_surcharge_tax2: bool
    custom_surcharge_tax3: bool
    custom_surcharge_tax4: bool
    line_items: list[Any]
    entity_type: str
    reminder1_sent: str
    reminder2_sent: str
    reminder3_sent: str
    reminder_last_sent: str
    paid_to_date: datetime
    subscription_id: str
    auto_bill_enabled: bool
    invitations: list[NinjaInvitations]  # [{}] was not full
    documents: list[Any]


class NinjaInvoice(object):
    """Ninja Invoice entity"""

    class Item:
        def __init__(self, data={}):
            self.data = data
            self.__data_keys = [k for k in data]
            for k in data:
                self.__setattr__(k, data[k])

        def to_dict(self):
            return {k: self.__getattribute__(k) for k in self.__data_keys}

    def __init__(self, data={}):
        self.__data_keys = [k for k in data]
        for k in data:
            self.__setattr__(k, data[k])

    def to_dict(self):
        return {k: self.__getattribute__(k) for k in self.__data_keys}

    @staticmethod
    def all():
        """gets list of invoices
        HTTP: GET ninja.test/api/v1/invoices -H "X-Ninja-Token: TOKEN"
        """
        log(log.DEBUG, "NinjaApi.invoices")
        res = api.do_get(api.BASE_URL + "invoices")
        res = ArrayData.parse_obj(res)
        invoices = [_NinjaInvoice.parse_obj(data) for data in res.data]
        next_link = api.get_next_link(res)
        while next_link:
            res = api.do_get(next_link)
            invoices += [NinjaInvoice(data) for data in res["data"]] if res else []
            next_link = api.get_next_link(res)
        return invoices

    @property
    def items(self):
        if "invoice_items" not in dir(self):
            return None
        return [NinjaInvoice.Item(data) for data in self.invoice_items]

    def add_item(self, product_key, notes, cost, qty=1):
        self.invoice_items += [
            {"product_key": product_key, "notes": notes, "cost": cost, "qty": qty}
        ]
        result = self.save()
        return result if result else None

    def delete_item(self, invoice_items):
        self.invoice_items = [
            data
            for data in self.invoice_items
            if data.get("notes") != invoice_items.get("notes")
        ]

    def save(self):
        log(log.DEBUG, "NinjaApi.update_invoice %d", self.id)
        api_result = api.do_put(
            "{}invoices/{}".format(api.BASE_URL, self.id), **(self.to_dict())
        )
        return api_result if api_result else None

    @staticmethod
    def get(invoice_id: int):  # noqa E999
        log(log.DEBUG, "NinjaInvoice.get %d", invoice_id)
        res = api.do_get("{}invoices?id={}".format(api.BASE_URL, invoice_id))
        if not res or not res["data"]:
            return res
        return NinjaInvoice(res["data"][0])

    @staticmethod
    def add(client_id, invoice_date, due_date=""):
        log(
            log.DEBUG,
            "NinjaInvoice.add client_id:%d %s:%s",
            client_id,
            invoice_date,
            due_date,
        )
        res = api.do_post(
            api.BASE_URL + "invoices",
            client_id=client_id,
            invoice_date=invoice_date,
            due_date=due_date,
        )
        if not res or not res["data"]:
            return res
        return _NinjaInvoice.parse_obj(res["data"])

    def delete(self):
        log(log.DEBUG, "NinjaInvoice.delete %d", self.id)
        return api.do_delete("{}invoices/{}".format(api.BASE_URL, self.id))
