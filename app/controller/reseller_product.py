from app.forms import ResellerProductForm
from app.models import ResellerProduct, HistoryChange


def check_and_set_history_changes(form: ResellerProductForm, product=ResellerProduct):
    if product.months != form.months.data:
        HistoryChange(
            change_type=HistoryChange.EditType.changes_reseller_product,
            item_id=product.product_id,
            value_name="months",
            before_value_str=str(product.months),
            after_value_str=str(form.months.data),
        ).save()
    if product.init_price != form.init_price.data:
        HistoryChange(
            change_type=HistoryChange.EditType.changes_reseller_product,
            item_id=product.product_id,
            value_name="init_price",
            before_value_str=str(product.init_price),
            after_value_str=str(form.init_price.data),
        ).save()
    if product.ext_price != form.ext_price.data:
        HistoryChange(
            change_type=HistoryChange.EditType.changes_reseller_product,
            item_id=product.product_id,
            value_name="ext_price",
            before_value_str=str(product.ext_price),
            after_value_str=str(form.ext_price.data),
        ).save()
