from datetime import datetime
from typing import Any
from pydantic import BaseModel

from app.logger import log


class NinjaClientContact(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    created_at: datetime
    updated_at: datetime
    archived_at: int
    is_primary: bool
    is_locked: bool
    phone: str
    custom_value1: str
    custom_value2: str
    custom_value3: str
    custom_value4: str
    contact_key: str
    send_email: bool
    last_login: int
    password: str
    link: str


class NinjaClientSettings(BaseModel):
    entity: str
    currency_id: int


class NinjaClient(BaseModel):
    id: str
    user_id: str
    assigned_user_id: str
    name: str
    website: str
    private_notes: str
    balance: float
    group_settings_id: str
    paid_to_date: datetime
    credit_balance: float
    last_login: datetime
    size_id: str
    public_notes: str
    client_hash: str
    address1: str
    address2: str
    phone: str
    city: str
    state: str
    postal_code: str
    country_id: str
    industry_id: str
    custom_value1: str
    custom_value2: str
    custom_value3: str
    custom_value4: str
    shipping_address1: str
    shipping_address2: str
    shipping_city: str
    shipping_state: str
    shipping_postal_code: str
    shipping_country_id: str
    settings: NinjaClientSettings
    is_deleted: bool
    vat_number: str
    id_number: str
    updated_at: datetime
    archived_at: datetime
    created_at: datetime
    display_name: str
    number: str
    contacts: list[NinjaClientContact]
    documents: list[Any]
    gateway_tokens: list[Any]

    def save(self):
        from app.ninja import api

        log(log.DEBUG, "Save NinjaClient [%s]", self.id)
        api_result = api.do_put(
            f"{api.BASE_URL}clients/{self.id}", **self.dict(exclude_none=True)
        )
        return NinjaClient.parse_obj(api_result["data"]) if api_result else None
