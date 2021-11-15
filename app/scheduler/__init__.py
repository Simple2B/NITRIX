from app.logger import log
from app.models import HistoryChange
from .methods import (
    creation_reseller_product,
    creation_reseller,
    creation_product,
    changes_reseller_product,
    changes_reseller,
)


_DISPATCHER_MAP = {
    HistoryChange.EditType.creation_reseller_product: creation_reseller_product,
    HistoryChange.EditType.creation_reseller: creation_reseller,
    HistoryChange.EditType.creation_product: creation_product,
    HistoryChange.EditType.changes_reseller_product: changes_reseller_product,
    HistoryChange.EditType.changes_reseller: changes_reseller,
}


def sync_scheduler():
    # TODO: fix docs
    """
    1. get current time and date
    2. get all needed invoices in some list (creation date is lower than current;
        filtered by HistoryChange.change_type creation, change;
        all in one list or separate?)
    3. go thru list with cycle and send each invoice
    4. if response ok, mark synced = True (if not try send again or go to next?)
    6.
    """
    log(log.INFO, "[SHED] Start sync scheduler")

    changes: list[HistoryChange] = HistoryChange.query.filter(
        HistoryChange.synced == False  # noqa E712
    ).all()
    log(log.INFO, "[SHED] Invoices: [%s]", changes)

    for change in changes:
        if change.change_type not in _DISPATCHER_MAP:
            log(
                log.WARNING,
                "[SHED] no method for a change [%s](%d)",
                change.change_type,
                change.id,
            )
            continue
        method = _DISPATCHER_MAP[change.change_type]
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
