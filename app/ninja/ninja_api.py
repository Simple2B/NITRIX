import os
import requests
import json
from typing import Any, Optional
from dotenv import load_dotenv
from pydantic import BaseModel

from app.logger import log
from .client import NinjaClient
from .product import NinjaProduct

load_dotenv()


class PaginationLinks(BaseModel):
    next: Optional[str]
    previous: Optional[str]


class Pagination(BaseModel):
    total: int
    count: int
    per_page: int
    current_page: int
    total_pages: int
    links: Optional[PaginationLinks]


class Meta(BaseModel):
    pagination: Pagination


class ArrayData(BaseModel):
    data: list[Any]
    meta: Meta


class NinjaApi(object):
    """Invoice Ninja API"""

    def __init__(self):
        super().__init__()
        # NINJA_API_BASE_URL=http://ec2-52-14-0-156.us-east-2.compute.amazonaws.com:8080/api/v1/
        self.BASE_URL = os.environ.get(
            "NINJA_API_BASE_URL",
            "",
        )
        self.NINJA_TOKEN = os.environ.get("NINJA_API_TOKEN", "")

    @property
    def configured(self):
        return True if self.BASE_URL else False

    def do_get(self, url: str):  # noqa E999
        headers = {"X-API-Token": self.NINJA_TOKEN}
        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            log(log.ERROR, "NinjaApi wrong NINJA_API_BASE_URL")
            return None
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            log(log.ERROR, "NinjaApi.HTTPError: %s", error)
        return response.json() if response.ok else None

    def do_post(self, url: str, **data):
        headers = {
            "X-API-Token": self.NINJA_TOKEN,
            "X-Requested-With": "XMLHttpRequest",
        }
        try:
            response = requests.post(url, headers=headers, data=data)
        except requests.exceptions.ConnectionError:
            log(log.ERROR, "NinjaApi wrong NINJA_API_BASE_URL")
            return None
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            log(log.ERROR, "NinjaApi.HTTPError: %s", error)
        return response.json() if response.ok else None

    def do_delete(self, url: str):
        headers = {"X-API-Token": self.NINJA_TOKEN}
        try:
            response = requests.delete(url, headers=headers)
        except requests.exceptions.ConnectionError:
            log(log.ERROR, "NinjaApi wrong NINJA_API_BASE_URL")
            return None
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            log(log.ERROR, "NinjaApi.HTTPError: %s", error)
        return response.json()

    def do_put(self, url: str, **data):
        headers = {
            "X-API-Token": self.NINJA_TOKEN,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
        }
        data = json.dumps(data)
        try:
            response = requests.put(url, headers=headers, data=data)
        except requests.exceptions.ConnectionError:
            log(log.ERROR, "NinjaApi wrong NINJA_API_BASE_URL")
            return None
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            log(log.ERROR, "NinjaApi.HTTPError: %s", error)
        return response.json() if response.ok else None

    @property
    def clients(self):
        """gets list of clients
        HTTP: GET ninja.test/api/v1/clients -H "X-API-Token: TOKEN"
        """
        log(log.DEBUG, "NinjaApi.clients")
        res = self.do_get(self.BASE_URL + "clients")
        res = ArrayData.parse_obj(res)
        clients = (
            [NinjaClient.parse_obj(client_data) for client_data in res.data]
            if res
            else []
        )
        next_link = NinjaApi.get_next_link(res)
        while next_link:
            res = self.do_get(next_link)
            res = ArrayData.parse_obj(res)
            clients += [NinjaClient.parse_obj(client_data) for client_data in res.data]
            next_link = NinjaApi.get_next_link(res)
        return clients

    def get_client(self, client_id: str):
        """gets client by id
            GET ninja.test/api/v1/clients?id_number=<value> -H "X-API-Token: TOKEN"
        Arguments:
            client_id {int} -- Invoice Ninja Client ID
        """
        log(log.DEBUG, "NinjaApi.get_client %s", client_id)
        res = self.do_get(f"{self.BASE_URL}clients/{client_id}")
        if not res or not res["data"]:
            return res
        return NinjaClient.parse_obj(res["data"])

    def add_client(self, name: str):
        """adds new client
            curl -X POST ninja.test/api/v1/clients -H "Content-Type:application/json" \
                -d '{"name":"Client"}' -H "X-API-Token: TOKEN"
        Arguments:
            name {str} -- Ninja Client Name
        """
        log(log.DEBUG, "NinjaApi.add_client %s", name)
        res = self.do_post(self.BASE_URL + "clients", name=name)
        if not res or not res["data"]:
            return res
        return NinjaClient.parse_obj(res["data"])

    def delete_client(self, client_id: str):
        """deletes client by id

        Arguments:
            client_id {int} -- Invoice Ninja Client ID
        """
        log(log.DEBUG, "NinjaApi.delete_client %s", client_id)
        return self.do_delete(f"{self.BASE_URL}clients/{client_id}")

    def update_client(self, client_id: str, name: str):
        log(log.DEBUG, "NinjaApi.update_client %s", client_id)
        return self.do_put(
            f"{self.BASE_URL}clients/{client_id}",
            id=client_id,
            name=name,
        )

    @staticmethod
    def get_next_link(response: ArrayData):
        pagination_links = response.meta.pagination.links
        if pagination_links:
            return pagination_links.next

    @property
    def products(self):
        """gets list of clients
        HTTP: GET ninja.test/api/v1/products -H "X-API-Token: TOKEN"
        """
        log(log.DEBUG, "NinjaApi.products")
        res = self.do_get(self.BASE_URL + "products")
        res = ArrayData.parse_obj(res)
        prods = [NinjaProduct.parse_obj(data) for data in res.data]
        next_link = NinjaApi.get_next_link(res)
        while next_link:
            res = self.do_get(next_link)
            res = ArrayData.parse_obj(res)
            prods += [NinjaProduct.parse_obj(data) for data in res.data]
            next_link = NinjaApi.get_next_link(res)
        return prods

    def get_product(self, prod_id: str):
        """gets client by id
            GET ninja.test/api/v1/clients?id_number=<value> -H "X-API-Token: TOKEN"
        Arguments:
            client_id {int} -- Invoice Ninja Client ID
        """
        log(log.DEBUG, "NinjaApi.get_product %s", prod_id)
        res = self.do_get(f"{self.BASE_URL}products/{prod_id}")
        if not res or not res["data"]:
            return res
        return NinjaProduct.parse_obj(res["data"])

    def add_product(self, notes: str, product_key: str, cost: float, qty: float = 1.0):
        """adds new product
            curl -X POST ninja.test/api/v1/products -H "Content-Type:application/json" \
                -d '{"notes":"Notes"}' -H "X-API-Token: TOKEN"
        Arguments:
            name {str} -- Ninja Client Name
        """
        log(
            log.DEBUG,
            "NinjaApi.add_product %s, %s, %f, %f",
            notes,
            product_key,
            cost,
            qty,
        )
        res = self.do_post(
            self.BASE_URL + "products",
            notes=notes,
            product_key=product_key,
            cost=cost,
            qty=qty,
        )
        if not res or not res["data"]:
            return res
        return NinjaProduct.parse_obj(res["data"])

    def update_product(
        self, prod_id: int, notes: str, product_key: str, cost: float, qty: float = 1.0
    ):
        """updates product by id

        Arguments:
            prod_id {int} -- product id
            notes {str} -- notes
            product_key {str} -- product name
            cost {float} -- price

        Keyword Arguments:
            qty {float} -- quantity (default: {1.0})

        Returns:
            Product -- product
        """
        log(log.DEBUG, "NinjaApi.update_product %s", prod_id)
        return self.do_put(
            "{}products/{}".format(self.BASE_URL, prod_id),
            id=prod_id,
            product_key=product_key,
            notes=notes,
            cost=cost,
            qty=qty,
        )

    def delete_product(self, prod_id: str):
        """deletes product by id (archive product)

        Arguments:
            prod_id {int} -- Invoice Ninja Product ID
        """
        res_data = self.do_delete(f"{self.BASE_URL}products/{prod_id}")
        return NinjaProduct.parse_obj(res_data["data"])
