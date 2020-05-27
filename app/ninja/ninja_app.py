import os
import requests
import json

from app.logger import log
from .client import NinjaClient
from .product import NinjaProduct


class NinjaApp(object):
    """ Invoice Ninja API """
    def __init__(self):
        super().__init__()
        self.BASE_URL = os.environ.get(
            'NINJA_API_BASE_URL', 'http://ec2-52-14-0-156.us-east-2.compute.amazonaws.com:8080/api/v1/')
        self.NINJA_TOKEN = os.environ.get(
            'NINJA_API_TOKEN', 'UNKNOWN_TOKEN')

    def do_get(self, url: str):
        headers = {'X-Ninja-Token': self.NINJA_TOKEN}
        response = requests.get(url, headers=headers)
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            log(log.ERROR, 'NinjaApp.HTTPError: %s', error)
        return response.json() if response.ok else None

    def do_post(self, url: str, **data):
        headers = {'X-Ninja-Token': self.NINJA_TOKEN}
        response = requests.post(url, headers=headers, data=data)
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            log(log.ERROR, 'NinjaApp.HTTPError: %s', error)
        return response.json() if response.ok else None

    def do_delete(self, url: str):
        headers = {'X-Ninja-Token': self.NINJA_TOKEN}
        response = requests.delete(url, headers=headers)
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            log(log.ERROR, 'NinjaApp.HTTPError: %s', error)
        return response.ok

    def do_put(self, url: str, **data):
        headers = {
            'X-Ninja-Token': self.NINJA_TOKEN,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
            }
        data = json.dumps(data)
        response = requests.put(url, headers=headers, data=data)
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            log(log.ERROR, 'NinjaApp.HTTPError: %s', error)
        return response.ok

    @property
    def clients(self):
        """gets list of clients
            HTTP: GET ninja.test/api/v1/clients -H "X-Ninja-Token: TOKEN"
        """
        log(log.DEBUG, 'NinjaApp.clients')
        res = self.do_get(self.BASE_URL + 'clients')
        return [NinjaClient(client_data) for client_data in res['data']]

    def get_client(self, client_id: int):
        """gets client by id
            GET ninja.test/api/v1/clients?id_number=<value> -H "X-Ninja-Token: TOKEN"
        Arguments:
            client_id {int} -- Invoice Ninja Client ID
        """
        log(log.DEBUG, 'NinjaApp.get_client %d', client_id)
        res = self.do_get('{}clients?id={}'.format(self.BASE_URL, client_id))
        if not res or not res['data']:
            return res
        return NinjaClient(res['data'][0])

    def add_client(self, name: str):
        """adds new client
            curl -X POST ninja.test/api/v1/clients -H "Content-Type:application/json" \
                -d '{"name":"Client"}' -H "X-Ninja-Token: TOKEN"
        Arguments:
            name {str} -- Ninja Client Name
        """
        log(log.DEBUG, 'NinjaApp.add_client %s', name)
        res = self.do_post(self.BASE_URL + 'clients', name=name)
        if not res or not res['data']:
            return res
        return NinjaClient(res['data'])

    def delete_client(self, client_id: int):
        """deletes client by id

        Arguments:
            client_id {int} -- Invoice Ninja Client ID
        """
        log(log.DEBUG, 'NinjaApp.delete_client %d', client_id)
        return self.do_delete('{}clients/{}'.format(self.BASE_URL, client_id))

    @property
    def products(self):
        """gets list of clients
            HTTP: GET ninja.test/api/v1/products -H "X-Ninja-Token: TOKEN"
        """
        log(log.DEBUG, 'NinjaApp.products')
        res = self.do_get(self.BASE_URL + 'products')
        return [NinjaProduct(data) for data in res['data']]

    def get_product(self, prod_id: int):
        """gets client by id
            GET ninja.test/api/v1/clients?id_number=<value> -H "X-Ninja-Token: TOKEN"
        Arguments:
            client_id {int} -- Invoice Ninja Client ID
        """
        log(log.DEBUG, 'NinjaApp.get_product %d', prod_id)
        res = self.do_get('{}products?id={}'.format(self.BASE_URL, prod_id))
        if not res or not res['data']:
            return res
        return NinjaProduct(res['data'][0])

    def add_product(self, notes: str, product_key: str, cost: float, qty: float = 1.0):
        """adds new product
            curl -X POST ninja.test/api/v1/products -H "Content-Type:application/json" \
                -d '{"notes":"Notes"}' -H "X-Ninja-Token: TOKEN"
        Arguments:
            name {str} -- Ninja Client Name
        """
        log(log.DEBUG, 'NinjaApp.add_product %s, %s, %f, %f', notes, product_key, cost, qty)
        res = self.do_post(
            self.BASE_URL + 'products', notes=notes, product_key=product_key, cost=cost, qty=qty)
        if not res or not res['data']:
            return res
        return NinjaProduct(res['data'])

    def delete_product(self, prod_id: int, product_key: str):
        """deletes product by id (archive product)

        Arguments:
            prod_id {int} -- Invoice Ninja Product ID
        """
        log(log.DEBUG, 'NinjaApp.delete_product %d', prod_id)
        return self.do_put(
            '{}products/{}?action=delete'.format(self.BASE_URL, prod_id), id=prod_id, product_key=product_key)
