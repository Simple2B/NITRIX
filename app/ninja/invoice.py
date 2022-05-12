from typing import Any, Optional
from pydantic import BaseModel
from app.logger import log
from app.ninja import api
from app.ninja.ninja_api import ArrayData


class NinjaInvitations(BaseModel):
    id: str
    client_contact_id: str
    key: str
    link: str
    sent_date: str
    viewed_date: str
    opened_date: str
    updated_at: int
    archived_at: int
    created_at: int
    email_status: str
    email_error: str


class NinjaInvoiceItem(BaseModel):
    product_key: str
    notes: str
    cost: float
    product_cost: Optional[float]
    quantity: int
    tax_name1: Optional[str]
    tax_rate1: Optional[float]
    tax_name2: Optional[str]
    tax_rate2: Optional[float]
    tax_name3: Optional[str]
    tax_rate3: Optional[float]
    custom_value1: Optional[str]
    custom_value2: Optional[str]
    custom_value3: Optional[str]
    discount: Optional[float]
    type_id: Optional[str]
    createdAt: Optional[int]
    is_amount_discount: Optional[bool]
    sort_id: Optional[str]
    line_total: Optional[float]
    gross_line_total: Optional[float]
    date: Optional[str]


class NinjaInvoice(BaseModel):
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
    created_at: int
    updated_at: int
    archived_at: int
    is_deleted: bool
    number: str
    discount: float
    po_number: str
    date: str
    last_sent_date: str
    next_send_date: str
    due_date: str
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
    exchange_rate: float
    custom_surcharge_tax1: bool
    custom_surcharge_tax2: bool
    custom_surcharge_tax3: bool
    custom_surcharge_tax4: bool
    line_items: list[NinjaInvoiceItem]
    entity_type: str
    reminder1_sent: str
    reminder2_sent: str
    reminder3_sent: str
    reminder_last_sent: str
    paid_to_date: int
    subscription_id: str
    auto_bill_enabled: bool
    invitations: list[NinjaInvitations]
    documents: list[Any]

    @staticmethod
    def all():
        """gets list of invoices
        HTTP: GET ninja.test/api/v1/invoices -H "X-Ninja-Token: TOKEN"
        """
        log(log.DEBUG, "NinjaApi.invoices")
        res = api.do_get(api.BASE_URL + "invoices")
        res = ArrayData.parse_obj(res)
        invoices = [NinjaInvoice.parse_obj(data) for data in res.data]
        next_link = api.get_next_link(res)
        while next_link:
            res = api.do_get(next_link)
            res = ArrayData.parse_obj(res)
            invoices += [NinjaInvoice.parse_obj(data) for data in res.data]
            next_link = api.get_next_link(res)
        return invoices

    def add_item(self, product_key, notes, cost, qty=1):
        new_item = NinjaInvoiceItem(
            product_key=product_key, notes=notes, cost=cost, quantity=qty
        )

        self.line_items += [new_item]

        return self.save()

    def delete_item(self, item: NinjaInvoiceItem):
        for i in self.line_items:
            if item.notes == i.notes:
                self.line_items.remove(i)
                break

    def update_item(self, item: NinjaInvoiceItem, note: str):
        for i in self.line_items:
            if item.notes == i.notes:
                item.notes = note
                break

    def save(self):
        log(log.DEBUG, "NinjaApi.update_invoice %s", self.id)
        api_result = api.do_put(
            f"{api.BASE_URL}invoices/{self.id}", **self.dict(exclude_none=True)
        )
        return NinjaInvoice.parse_obj(api_result["data"]) if api_result else None

    @staticmethod
    def get(invoice_id: str):
        log(log.DEBUG, "NinjaInvoice.get [%s]", invoice_id)
        res = api.do_get(f"{api.BASE_URL}invoices/{invoice_id}")
        if not res or not res["data"]:
            return res
        return NinjaInvoice.parse_obj(res["data"])

    @staticmethod
    def add(client_id, invoice_date, due_date=""):
        log(
            log.DEBUG,
            "NinjaInvoice.add client_id:[%s] [%s]:[%s]",
            client_id,
            invoice_date,
            due_date,
        )
        res = api.do_post(
            api.BASE_URL + "invoices",
            client_id=client_id,
            date=invoice_date,
            due_date=due_date,
        )
        if not res or not res["data"]:
            return res
        return NinjaInvoice.parse_obj(res["data"])

    def delete(self):
        log(log.DEBUG, "NinjaInvoice.delete [%s]", self.id)
        return api.do_delete(f"{api.BASE_URL}invoices/{self.id}")
