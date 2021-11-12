from datetime import datetime
from typing import Any
from pydantic import BaseModel


class NinjaProduct(BaseModel):
    """Ninja Product entity"""

    id: str
    user_id: str
    assigned_user_id: str
    product_key: str
    notes: str
    cost: float
    price: float
    quantity: float
    tax_name1: str
    tax_rate1: float
    tax_name2: str
    tax_rate2: float
    tax_name3: str
    tax_rate3: float
    created_at: datetime
    updated_at: datetime
    archived_at: datetime
    custom_value1: str
    custom_value2: str
    custom_value3: str
    custom_value4: str
    is_deleted: bool
    documents: list[Any]
