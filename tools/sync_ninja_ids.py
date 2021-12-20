import re

from app.ninja import api as ninja
from app.ninja.client import NinjaClient
from app.ninja.product import NinjaProduct
from app.models import Reseller, Phone, ResellerProduct, Product
from sqlalchemy import and_

from app.logger import log
from app import db


PHONE_PREFIX = "Phone-"
PATTERN = re.compile(r"^(?P<prod_name>[\w\s-]*)\s(?P<months>[\d]+)\sMonths$")


def sync_ninja_clients():
    for client in ninja.clients:
        client: NinjaClient = client
        reseller: Reseller = Reseller.query.filter(Reseller.name == client.name).first()
        if not reseller:
            log(log.WARNING, "Cannot find reseller by name [%s]", client.name)
            continue
        reseller.ninja_client_id = client.id
        if client.is_deleted != reseller.deleted:
            log(
                log.WARNING,
                "[%s]: client.deleted[%s] != reseller.deleted[%s]",
                client.name,
                client.is_deleted,
                reseller.deleted,
            )
        reseller.save(False)
    db.session.commit()
    for reseller in Reseller.query.all():
        reseller: Reseller = reseller
        if not reseller.ninja_client_id:
            log(log.WARNING, "Reseller [%s] has not ninja_client_id", reseller.name)


def sync_ninja_products():
    for prod in ninja.products:
        prod: NinjaProduct = prod
        is_phone = prod.product_key.startswith(PHONE_PREFIX)
        if is_phone:
            prefix_len = len(PHONE_PREFIX)
            name = prod.product_key[prefix_len:]
            phone: Phone = Phone.query.filter(Phone.name == name).first()
            if phone:
                phone.ninja_product_id = prod.id
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
            reseller_product.ninja_product_id = prod.id
            reseller_product.save(False)
    db.session.commit()
