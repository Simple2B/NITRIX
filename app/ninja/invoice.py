from app.logger import log
from app.ninja import api


class NinjaInvoice(object):
    """Ninja Invoice entity"""

    class Item:
        def __init__(self, data={}):
            self.data = data
            self.__data_keys = [k for k in data]
            for k in data:
                self.__setattr__(k, data[k])

        def to_dict(self):
            return {k: self.__getattribute__(k) for k in self.__data_keys}

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
        log(log.DEBUG, "NinjaApi.invoices")
        res = api.do_get(api.BASE_URL + "invoices")
        invoices = [NinjaInvoice(data) for data in res["data"]] if res else []
        next_link = api.get_next_link(res)
        while next_link:
            res = api.do_get(next_link)
            invoices += [NinjaInvoice(data) for data in res["data"]] if res else []
            next_link = api.get_next_link(res)
        return invoices

    @property
    def items(self):
        if "invoice_items" not in dir(self):
            return None
        return [NinjaInvoice.Item(data) for data in self.invoice_items]

    def add_item(self, product_key, notes, cost, qty=1):
        self.invoice_items += [
            {"product_key": product_key, "notes": notes, "cost": cost, "qty": qty}
        ]
        result = self.save()
        return result if result else None

    def delete_item(self, invoice_items):
        self.invoice_items = [
            data
            for data in self.invoice_items
            if data["invoice_items"] != invoice_items
        ]

    def save(self):
        log(log.DEBUG, "NinjaApi.update_product %d", self.id)
        api_result = api.do_put(
            "{}invoices/{}".format(api.BASE_URL, self.id), **(self.to_dict())
        )
        return api_result if api_result else None

    @staticmethod
    def get(invoice_id: int):  # noqa E999
        log(log.DEBUG, "NinjaInvoice.get %d", invoice_id)
        res = api.do_get("{}invoices?id={}".format(api.BASE_URL, invoice_id))
        if not res or not res["data"]:
            return res
        return NinjaInvoice(res["data"][0])

    @staticmethod
    def add(client_id, invoice_date, due_date=""):
        log(
            log.DEBUG,
            "NinjaInvoice.add client_id:%d %s:%s",
            client_id,
            invoice_date,
            due_date,
        )
        res = api.do_post(
            api.BASE_URL + "invoices",
            client_id=client_id,
            invoice_date=invoice_date,
            due_date=due_date,
        )
        if not res or not res["data"]:
            return res
        return NinjaInvoice(res["data"])

    def delete(self):
        log(log.DEBUG, "NinjaInvoice.delete %d", self.id)
        return api.do_delete("{}invoices/{}".format(api.BASE_URL, self.id))
