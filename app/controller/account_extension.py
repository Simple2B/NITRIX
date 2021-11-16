from dateutil.relativedelta import relativedelta
from app.forms import AccountExtensionForm
from app.models import AccountExtension, HistoryChange


def check_and_set_history_changes(
    form: AccountExtensionForm, extension: AccountExtension
):

    if extension.reseller_id != form.reseller_id.data:
        HistoryChange(
            change_type=HistoryChange.EditType.extensions_account_change,
            item_id=extension.id,
            value_name="reseller",
            before_value_str=str(extension.reseller_id),
            after_value_str=str(form.reseller_id.data),
        ).save()
    if extension.product_id != form.product_id.data:
        HistoryChange(
            change_type=HistoryChange.EditType.extensions_account_change,
            item_id=extension.id,
            value_name="product",
            before_value_str=str(extension.product_id),
            after_value_str=str(form.product_id.data),
        ).save()
    if extension.months != form.months.data:
        HistoryChange(
            change_type=HistoryChange.EditType.extensions_account_change,
            item_id=extension.id,
            value_name="months",
            before_value_str=str(extension.months),
            after_value_str=str(form.months.data),
        ).save()
    if extension.extension_date != form.extension_date.data:
        HistoryChange(
            change_type=HistoryChange.EditType.extensions_account_change,
            item_id=extension.id,
            value_name="extension_date",
            before_value_str=str(extension.extension_date),
            after_value_str=str(form.extension_date.data),
        ).save()

    # we need this??
    if extension.end_date != extension.extension_date + relativedelta(
        months=extension.months
    ):
        HistoryChange(
            change_type=HistoryChange.EditType.extensions_account_change,
            item_id=extension.id,
            value_name="end_date",
            before_value_str=str(extension.end_date),
            after_value_str=str(
                extension.extension_date + relativedelta(months=extension.months)
            ),
        ).save()
