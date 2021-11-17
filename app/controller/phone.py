from app.forms import PhoneForm
from app.models import Phone, HistoryChange


def update_phone_history(form: PhoneForm, phone: Phone):
    if phone.name != form.name.data:
        HistoryChange(
            change_type=HistoryChange.EditType.changes_phone,
            item_id=phone.id,
            value_name="name",
            before_value_str=str(phone.name),
            after_value_str=str(form.name.data),
        ).save()
    if phone.status != form.status.data:
        HistoryChange(
            change_type=HistoryChange.EditType.changes_phone,
            item_id=phone.id,
            value_name="status",
            before_value_str=str(phone.status),
            after_value_str=str(form.status.data),
        ).save()
    if phone.price != form.price.data:
        HistoryChange(
            change_type=HistoryChange.EditType.changes_phone,
            item_id=phone.id,
            value_name="price",
            before_value_str=str(phone.price),
            after_value_str=str(form.price.data),
        ).save()
