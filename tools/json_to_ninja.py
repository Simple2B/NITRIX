from .ninja_to_json import NinjaClientModel, NinjaProductModel, NinjaInvoicesModel
from .read_json import read_json
from app.ninja.client import NinjaClient
from app.ninja import api as ninja


def get_ninja_clients():
    for json_client in read_json("ninja_clients"):
        client: NinjaClientModel = NinjaClientModel.parse_obj(json_client)
        assert client
        ninja_client = ninja.add_client(client.name)
        ninja_client.is_deleted = client.is_deleted
        if client.contacts:
            if ninja_client.contacts:
                contact = ninja_client.contacts[0]
                contact.contact_key = client.contacts
                account_key: str
                email: str
                id: int
                is_owner: bool
                contact_key: str
                is_primary: bool
                send_invoice: bool
        ninja_client.save()
