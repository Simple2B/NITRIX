from app.logger import log
from app.models import HistoryChange
from .methods import (
    creation_reseller_product,
    creation_reseller,
    creation_product,
    changes_reseller_product,
    changes_reseller,
    extension_account_new,
    extensions_account_change,
    changes_account,
    creation_account,
    creation_phone,
    changes_phone,
    deletion_phone,
)

# changes_product : changes_product
# deletion_phone_delete : deletion_phone_delete
# creation_phone:creation_phone
# changes_phone:changes_phone

_DISPATCHER_MAP = {
    HistoryChange.EditType.creation_reseller_product: creation_reseller_product,  # +
    HistoryChange.EditType.creation_reseller: creation_reseller,  # +
    HistoryChange.EditType.creation_product: creation_product,  # +
    HistoryChange.EditType.changes_reseller_product: changes_reseller_product,  # +
    HistoryChange.EditType.changes_reseller: changes_reseller,  # +
    HistoryChange.EditType.extension_account_new: extension_account_new,  # +
    HistoryChange.EditType.extensions_account_change: extensions_account_change,
    HistoryChange.EditType.changes_account: changes_account,  # pass
    HistoryChange.EditType.creation_account: creation_account,  # +
    HistoryChange.EditType.creation_phone: creation_phone,  # +
    HistoryChange.EditType.changes_phone: changes_phone,  # +
    HistoryChange.EditType.deletion_phone: deletion_phone,  # +
}


def sync_scheduler():
    """
    0. With periodic time call this scheduler (time sets in .env)
    1. get current changes: list[HistoryChange] where synced is False
    2. If no such changes we stop
    3. go thru changes with cycle and if its in _DISPATCHER_MAP we call its method
    4. if method return True, mark change as synced = True
    """
    log(log.DEBUG, ".")

    changes: list[HistoryChange] = HistoryChange.query.filter(
        HistoryChange.synced == False  # noqa E712
    ).all()
    len_changes = len(changes)
    if not changes:
        return
    log(log.INFO, "[SHED] Found [%d] changes", len_changes)

    log(log.INFO, "[SHED] Start sync scheduler")
    for change in changes:
        change: HistoryChange = change
        if change.change_type not in _DISPATCHER_MAP:
            log(
                log.WARNING,
                "[SHED] no method for a change [%s](%d)",
                change.change_type,
                change.id,
            )
            change.synced = True
            change.save()
            continue
        method = _DISPATCHER_MAP[change.change_type]
        log(log.INFO, "[SHED] Change: [%s]", change.change_type)
        if method(change):
            change.synced = True
            change.save()
        else:
            log(
                log.WARNING,
                "[SHED] method [%s](%d) returns False",
                change.change_type,
                change.id,
            )

    log(log.INFO, "[SHED] Finished sync scheduler")
