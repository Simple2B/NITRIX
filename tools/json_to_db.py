# from datetime import datetime
# from typing import Optional
from pydantic import BaseModel

# from sqlalchemy import and_
from app.database import db
from app.logger import log
from app.models import (  # noqa 401
    User,
    Reseller,
    ResellerProduct,
    Phone,
    Product,
    Account,
    AccountExtension,
    HistoryChange,
)
from .read_json import read_json


class PhoneModel(BaseModel):
    name: str
    status: Phone.Status
    price: float

    class Config:
        orm_mode = True
        use_enum_values = True


class ProductModel(BaseModel):
    name: str
    status: Product.Status

    class Config:
        orm_mode = True
        use_enum_values = True


class ResellerModel(BaseModel):

    name: str
    status: Reseller.Status
    comments: str

    class Config:
        orm_mode = True
        use_enum_values = True


# class ResellerProductModel(BaseModel):
#     months: int
#     init_price: float
#     ext_price: float
#     reseller: ResellerModel
#     product: ProductModel

#     class Config:
#         orm_mode = True
#         use_enum_values = True


# class AccountModel(BaseModel):
#     name: str
#     sim: str
#     imei: str
#     comment: str
#     activation_date: datetime
#     months: int
#     product: ProductModel
#     phone: PhoneModel
#     reseller: ResellerModel

#     class Config:
#         orm_mode = True
#         use_enum_values = True


# class AccountExtensionModel(BaseModel):
#     extension_date: datetime
#     end_date: datetime
#     months: int
#     reseller: ResellerModel
#     product: ProductModel
#     account: Optional[AccountModel] = None

#     class Config:
#         orm_mode = True
#         use_enum_values = True


class UserModel(BaseModel):
    name: str
    user_type: User.Type
    password_hash: str
    activated: User.Status
    otp_secret: str
    otp_active: bool

    class Config:
        orm_mode = True
        use_enum_values = True


# class AccountChangesModel(BaseModel):
#     date: datetime
#     change_type: AccountChanges.ChangeType
#     value_str: Optional[str] = None
#     new_value_str: Optional[str] = None
#     account: Optional[AccountModel] = None
#     user: UserModel

#     class Config:
#         orm_mode = True
#         use_enum_values = True


def get_phones():
    phones = read_json("phones")
    log(log.DEBUG, "[GET phones from file] Got [%d] phones!", len(phones))
    for phone in phones:
        phone: PhoneModel = PhoneModel.parse_obj(phone)
        Phone(
            name=phone.name,
            status=Phone.Status(phone.name),
            price=phone.price,
        ).save(commit=False)
    db.session.commit()
    log(log.DEBUG, "[GET phones from file] Done!", len(phones))


def get_users():
    users = read_json("users")
    log(log.DEBUG, "[GET users from file] Got [%d] users!", len(users))
    for user in users:
        user_model: UserModel = Reseller.parse_obj(user)
        User(
            name=user_model.name,
            user_type=User.Type[user_model.user_type],
            password_hash=user_model.password_hash,
            activated=User.Status(user_model.activated),
            otp_secret=user_model.otp_secret,
            otp_active=user_model.otp_active,
        ).save(commit=False)
    db.session.commit()
    log(log.DEBUG, "[GET users from file] Done! [%s]", len(users))


def get_resellers():
    resellers = read_json("resellers")
    log(log.DEBUG, "[GET resellers from file] Got [%d] resellers!", len(resellers))
    for reseller in resellers:
        reseller_model: ResellerModel = ResellerModel.parse_obj(reseller)
        # TODO : check len of reseller comments
        Reseller(
            name=reseller_model.name,
            status=Reseller.Status(reseller_model.status),
            comments=reseller_model.comments
            if len(reseller_model.comments) < 60
            else reseller_model.comments[0:59],
        ).save(commit=False)
    db.session.commit()
    resellers = Reseller.query.all()
    log(log.DEBUG, "[GET resellers from file] Done! [%s]", len(resellers))


def get_products():
    products = read_json("products")
    log(log.DEBUG, "[GET products from file] Got [%d] products!", len(products))
    for product in products:
        product_model: ProductModel = ProductModel.parse_obj(product)
        Product(
            name=product_model.name,
            status=Product.Status(product_model.status),
        ).save(commit=False)
    db.session.commit()
    log(log.DEBUG, "[GET products from file] Done! [%s]", len(products))
