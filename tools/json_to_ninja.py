from .ninja_to_json import NinjaClientModel, NinjaProductModel, NinjaInvoicesModel
from .read_json import read_json
from app.ninja.client import NinjaClient
from app.ninja import api as ninja

from app.logger import log


def get_ninja_clients():
    for json_client in read_json("ninja_clients"):
        client: NinjaClientModel = NinjaClientModel.parse_obj(json_client)
        assert client
        ninja_client = ninja.add_client(client.name)
        ninja_client.is_deleted = client.is_deleted
        if client.contacts:
            if ninja_client.contacts:
                contact_origin = client.contacts[0]
                contact = ninja_client.contacts[0]
                contact.contact_key = contact_origin.contact_key
                contact.email = contact_origin.email
                contact.is_primary = contact_origin.is_primary
                contact.send_email = contact_origin.send_invoice
            else:
                log(log.WARNING, "[get_ninja_clients] not found create contact info")
        else:
            log(log.WARNING, "[get_ninja_clients] cannot create contact info")
        ninja_client.save()
