from app.forms import PhoneForm
from app.models import Phone, HistoryChange


def check_and_set_history_changes(form: PhoneForm, product: Phone):
    if product.name != form.name.data:
        HistoryChange(
            change_type=HistoryChange.EditType.changes_phone,
            item_id=product.id,
            value_name="name",
            before_value_str=str(product.name),
            after_value_str=str(form.name.data),
        ).save()
    if product.status != form.status.data:
        HistoryChange(
            change_type=HistoryChange.EditType.changes_phone,
            item_id=product.id,
            value_name="status",
            before_value_str=str(product.status),
            after_value_str=str(form.status.data),
        ).save()
    if product.price != form.price.data:
        HistoryChange(
            change_type=HistoryChange.EditType.changes_phone,
            item_id=product.id,
            value_name="price",
            before_value_str=str(product.price),
            after_value_str=str(form.price.data),
        ).save()
