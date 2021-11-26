from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import and_
from app.logger import log
from app.models import (
    User,
    Reseller,
    ResellerProduct,
    Phone,
    Product,
    Account,
    AccountExtension,
    AccountChanges,
)
from .write_json import write_json, OutData


class PhoneModel(BaseModel):
    name: str
    status: Phone.Status
    price: float
    deleted: bool

    class Config:
        orm_mode = True
        use_enum_values = True


class ProductModel(BaseModel):
    name: str
    status: Product.Status
    deleted: bool

    class Config:
        orm_mode = True
        use_enum_values = True


class ResellerModel(BaseModel):

    name: str
    status: Reseller.Status
    comments: str
    deleted: bool

    class Config:
        orm_mode = True
        use_enum_values = True


class ResellerProductModel(BaseModel):
    months: int
    init_price: float
    ext_price: float
    reseller: ResellerModel
    product: ProductModel

    class Config:
        orm_mode = True
        use_enum_values = True


class AccountModel(BaseModel):
    name: str
    sim: str
    imei: str
    comment: str
    activation_date: datetime
    months: int
    product: ProductModel
    phone: PhoneModel
    reseller: ResellerModel
    deleted: bool

    class Config:
        orm_mode = True
        use_enum_values = True


class AccountExtensionModel(BaseModel):
    extension_date: datetime
    end_date: datetime
    months: int
    reseller: ResellerModel
    product: ProductModel
    account: Optional[AccountModel] = None

    class Config:
        orm_mode = True
        use_enum_values = True


class UserModel(BaseModel):
    name: str
    user_type: User.Type
    password_hash: str
    activated: User.Status
    otp_secret: str
    otp_active: bool
    deleted: bool

    class Config:
        orm_mode = True
        use_enum_values = True


class AccountChangesModel(BaseModel):
    date: datetime
    change_type: AccountChanges.ChangeType
    value_str: Optional[str] = None
    new_value_str: Optional[str] = None
    account: Optional[AccountModel] = None
    user: UserModel

    class Config:
        orm_mode = True
        use_enum_values = True


def get_users():
    users = User.query.filter(User.name != "admin").all()
    log(log.DEBUG, "[GET users from db]Got [%d] users!", len(users))
    write_json("users", OutData(data=[UserModel.from_orm(user) for user in users]))


def get_resellers():
    resellers = Reseller.query.filter(Reseller.name != "NITRIX").all()

    log(log.DEBUG, "[GET resellers from db]Got [%d] resellers!", len(resellers))
    write_json(
        "resellers",
        OutData(data=[ResellerModel.from_orm(reseller) for reseller in resellers]),
    )


def get_reseller_products():
    reseller_products = ResellerProduct.query.all()
    log(
        log.DEBUG,
        "[GET reseller_products from db]Got [%d] reseller_products!",
        len(reseller_products),
    )
    write_json(
        "reseller_products",
        OutData(
            data=[
                ResellerProductModel.from_orm(res_prod)
                for res_prod in reseller_products
            ]
        ),
    )


def get_products():
    products = Product.query.all()
    log(log.DEBUG, "[GET products from db]Got [%d] products!", len(products))
    write_json(
        "products",
        OutData(data=[ProductModel.from_orm(product) for product in products]),
    )


def get_phones():
    phones = Phone.query.filter(Phone.name != "None").all()
    log(log.DEBUG, "[GET phones from db]Got [%d] phones!", len(phones))
    write_json("phones", OutData(data=[PhoneModel.from_orm(phone) for phone in phones]))


def get_accounts():
    accounts = Account.query.all()
    log(log.DEBUG, "[GET accounts from db] Got [%s] accounts!", len(accounts))
    write_json(
        "accounts",
        OutData(data=[AccountModel.from_orm(account) for account in accounts]),
    )


def get_account_ext():
    accounts_ext = AccountExtension.query.all()
    log(
        log.DEBUG,
        "[GET accounts_ext from db] Got [%d] accounts_ext!",
        len(accounts_ext),
    )
    write_json(
        "accounts_ext",
        OutData(
            data=[AccountExtensionModel.from_orm(acc_ext) for acc_ext in accounts_ext]
        ),
    )


def get_account_changes():

    accounts_changes = AccountChanges.query.all()
    log(
        log.DEBUG,
        "[GET accounts_changes from db]Got [%s] accounts_changes!",
        len(accounts_changes),
    )
    write_json(
        "accounts_changes",
        OutData(
            data=[
                AccountChangesModel.from_orm(acc_change)
                for acc_change in accounts_changes
            ]
        ),
    )
