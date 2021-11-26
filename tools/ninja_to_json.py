from pydantic import BaseModel
from app.logger import log
from app.ninja import NinjaApi, NinjaInvoice
from .write_json import write_json, OutData

api = NinjaApi()


# PRODUCT MODEL
class NinjaProductModel(BaseModel):
    product_key: str
    notes: str
    cost: float
    is_deleted: bool


# line_items FOR INVOICE MODEL
class NinjaInvoiceItem(BaseModel):
    product_key: str
    notes: str
    cost: float
    qty: int


# INVOICE MODEL
class NinjaInvoicesModel(BaseModel):
    client_id: int
    invoice_date: str
    due_date: str
    invoice_status_id: int
    amount: int
    balance: float
    has_tasks: bool
    has_expenses: bool
    updated_at: int
    invoice_items: list[NinjaInvoiceItem]

    class Config:
        use_enum_values = True


# contacts for Client
class NinjaClientContact(BaseModel):
    account_key: str
    email: str
    id: int
    is_owner: bool
    contact_key: str
    is_primary: bool
    send_invoice: bool


# CLIENT MODEL
class NinjaClientModel(BaseModel):
    id: int
    name: str
    display_name: str
    contacts: list[NinjaClientContact]
    is_deleted: bool

    class Config:
        use_enum_values = True


def get_ninja_clients():
    clients = [c for c in api.clients]
    log(log.DEBUG, "[GET clients from Ninja] Got [%d] clients!", len(clients))
    write_json(
        "ninja_clients",
        OutData(
            data=[NinjaClientModel.parse_obj(client.to_dict()) for client in clients]
        ),
    )


def get_ninja_products():
    products = [p for p in api.products]
    log(log.DEBUG, "[GET products from Ninja] Got [%d] products!", len(products))
    write_json(
        "ninja_products",
        OutData(
            data=[
                NinjaProductModel.parse_obj(product.to_dict()) for product in products
            ]
        ),
    )


def get_ninja_invoices():
    invoices = [i for i in NinjaInvoice.all() if not i.is_deleted]
    log(log.DEBUG, "[GET invoices from Ninja] Got [%d] invoices!", len(invoices))
    write_json(
        "ninja_invoices",
        OutData(
            data=[
                NinjaInvoicesModel.parse_obj(invoice.to_dict()) for invoice in invoices
            ]
        ),
    )
