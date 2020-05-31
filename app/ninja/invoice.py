from app.logger import log
from app.ninja import api


class NinjaInvoice(object):
    """Ninja Invoice entity
    """
    def __init__(self, data={}):
        self.__data_keys = [k for k in data]
        for k in data:
            self.__setattr__(k, data[k])

    def to_dict(self):
        return {k: self.__getattribute__(k) for k in self.__data_keys}

    @staticmethod
    def all():
        """gets list of invoices
            HTTP: GET ninja.test/api/v1/invoices -H "X-Ninja-Token: TOKEN"
        """
        log(log.DEBUG, 'NinjaApi.invoices')
        res = api.do_get(api.BASE_URL + 'invoices')
        return [NinjaInvoice(data) for data in res['data']] if res else []

    @property
    def items(self):
        return self.invoice_items if 'invoice_items' in dir(self) else None
