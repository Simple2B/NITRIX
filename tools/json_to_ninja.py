import re

from .ninja_to_json import (
    NinjaClientModel,
    NinjaProductModel,
    NinjaInvoicesModel,
    NinjaInvoiceItem as NinjaInvoiceItemModel,
)
from .read_json import read_json
from app.ninja import api as ninja
from app.ninja import NinjaInvoice
from app.ninja.invoice import NinjaInvoiceItem
from app.ninja.client import NinjaClient
from app.models import Reseller, Phone, ResellerProduct, Product
from sqlalchemy import and_

from app.logger import log
from app import db


PHONE_PREFIX = "Phone-"
PATTERN = re.compile(r"^(?P<prod_name>[\w\s-]*)\s(?P<months>[\d]+)\sMonths$")


def get_ninja_clients():
    for json_client in read_json("ninja_clients"):
        client: NinjaClientModel = NinjaClientModel.parse_obj(json_client)
        assert client
        if not client.name:
            continue
        ninja_client = ninja.add_client(client.name)
        ninja_client.is_deleted = client.is_deleted
        reseller: Reseller = Reseller.query.filter(Reseller.name == client.name).first()
        if reseller:
            reseller.ninja_client_id = ninja_client.id
            reseller.save(False)
        else:
            log(
                log.WARNING,
                "[get_ninja_clients] cannot found resseller by name: [%s]",
                client.name,
            )

        if client.contacts:
            if ninja_client.contacts:
                contact_origin = client.contacts[0]
                contact = ninja_client.contacts[0]
                contact.contact_key = contact_origin.contact_key
                contact.email = contact_origin.email
                contact.is_primary = contact_origin.is_primary
                contact.send_email = contact_origin.send_invoice
            else:
                log(log.WARNING, "[get_ninja_clients] not found create contact info")
        else:
            log(log.WARNING, "[get_ninja_clients] cannot create contact info")
        ninja_client.save(False)

    db.session.commit()


def dddd():
    for p in ninja.products:
        ninja.delete_product(p.id)


def get_ninja_products():
    # dddd()
    for json_prod in read_json("ninja_products"):
        prod: NinjaProductModel = NinjaProductModel.parse_obj(json_prod)
        assert prod.product_key
        ninja_prod = ninja.add_product(
            notes=prod.notes, product_key=prod.product_key, cost=prod.cost
        )
        if prod.is_deleted:
            ninja.delete_product(ninja_prod.id)
        is_phone = prod.product_key.startswith(PHONE_PREFIX)
        if is_phone:
            prefix_len = len(PHONE_PREFIX)
            name = prod.product_key[prefix_len:]
            phone: Phone = Phone.query.filter(Phone.name == name).first()
            if phone:
                phone.ninja_product_id = ninja_prod.id
                phone.save(False)
            else:
                log(log.WARNING, "[get_ninja_products] cannot found phone [%s]", name)
        else:
            reseller_name = prod.notes
            match = PATTERN.match(prod.product_key)
            if not match:
                log(
                    log.WARNING,
                    "[get_ninja_products] wrong product_key [%s]",
                    prod.product_key,
                )
                continue
            prod_name = match.group("prod_name")
            months = int(match.group("months"))

            reseller = Reseller.query.filter(Reseller.name == reseller_name).first()
            if not reseller:
                continue
            db_prod = Product.query.filter(Product.name == prod_name).first()
            if not db_prod:
                continue
            reseller_product: ResellerProduct = ResellerProduct.query.filter(
                and_(
                    ResellerProduct.product_id == db_prod.id,
                    ResellerProduct.reseller_id == reseller.id,
                    ResellerProduct.months == months,
                )
            ).first()
            if not reseller_product:
                continue
            reseller_product.ninja_product_id = ninja_prod.id
            reseller_product.save(False)
    db.session.commit()


def get_ninja_invoices():
    clients: list[NinjaClientModel] = [
        NinjaClientModel.parse_obj(c) for c in read_json("ninja_clients")
    ]

    ninja_clients = ninja.clients

    def find_client_by_id(id: int) -> NinjaClient:
        for c in clients:
            if c.id == id:
                for n_c in ninja_clients:
                    if n_c.name == c.name:
                        return n_c

    for json_invoice in read_json("ninja_invoices"):
        invoice: NinjaInvoicesModel = NinjaInvoicesModel.parse_obj(json_invoice)
        assert invoice
        client = find_client_by_id(invoice.client_id)
        assert client
        ninja_invoice: NinjaInvoice = NinjaInvoice.add(
            client_id=client.id,
            invoice_date=invoice.invoice_date,
            due_date=invoice.due_date,
        )
        for item in invoice.invoice_items:
            item: NinjaInvoiceItemModel = item
            assert item
            ninja_invoice.line_items += [
                NinjaInvoiceItem(
                    product_key=item.product_key,
                    notes=item.notes,
                    cost=item.cost,
                    quantity=1,
                    product_cost=item.cost,
                )
            ]
        ninja_invoice.save()
