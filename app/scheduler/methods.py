from app.models import HistoryChange, Reseller, ResellerProduct
from app.ninja import api as ninja
from app.utils import ninja_product_name
from app.logger import log


def creation_reseller_product(change: HistoryChange):
    assert change.change_type == HistoryChange.EditType.creation_reseller_product
    reseller_product: ResellerProduct = ResellerProduct.query.get(change.item_id)
    product_key = ninja_product_name(
        reseller_product.product.name, reseller_product.months
    )
    for prod in ninja.products:
        if prod.product_key == product_key:
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


def creation_product(change: HistoryChange):
    # creation product does not change InvoiceNinja
    return True
