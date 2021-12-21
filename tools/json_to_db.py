import enum
from datetime import datetime
from typing import Optional
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


class ChangeType(enum.Enum):
    sim = "SIM"
    name = "Name"
    imei = "IMEI"
    product = "Product"
    phone = "Phone"
    reseller = "Reseller"
    months = "Months"
    activation_date = "Activation date"
    created = "Created"
    deleted = "Deleted"


class AccountChangesModel(BaseModel):
    date: datetime
    change_type: ChangeType
    value_str: Optional[str] = None
    new_value_str: Optional[str] = None
    account: Optional[AccountModel] = None
    user: UserModel

    class Config:
        orm_mode = True
        use_enum_values = True


def get_phones():
    phones = read_json("phones")
    log(log.DEBUG, "[GET phones from file] Got [%d] phones!", len(phones))
    for phone in phones:
        phone: PhoneModel = PhoneModel.parse_obj(phone)
        Phone(
            name=phone.name,
            status=Phone.Status(phone.status),
            price=phone.price,
        ).save(commit=False)
    db.session.commit()
    log(log.DEBUG, "[GET phones from file] Done!")


def get_users():
    users = read_json("users")
    log(log.DEBUG, "[GET users from file] Got [%d] users!", len(users))
    for user in users:
        user_model: UserModel = UserModel.parse_obj(user)
        User(
            name=user_model.name,
            user_type=User.Type[user_model.user_type],
            password_hash=user_model.password_hash,
            activated=User.Status(user_model.activated),
            otp_secret=user_model.otp_secret,
            otp_active=user_model.otp_active,
        ).save(commit=False)
    db.session.commit()
    log(log.DEBUG, "[GET users from file] Done!")


def get_resellers():
    resellers = read_json("resellers")
    log(log.DEBUG, "[GET resellers from file] Got [%d] resellers!", len(resellers))
    for reseller in resellers:
        reseller_model: ResellerModel = ResellerModel.parse_obj(reseller)
        Reseller(
            name=reseller_model.name,
            status=Reseller.Status(reseller_model.status),
            comments=reseller_model.comments,
        ).save(commit=False)
    db.session.commit()
    resellers = Reseller.query.all()
    log(log.DEBUG, "[GET resellers from file] Done! ")


def get_products():
    products = read_json("products")
    log(log.DEBUG, "[GET products from file] Got [%d] products!", len(products))
    for product in products:
        product_model: ProductModel = ProductModel.parse_obj(product)
        Product(
            name=product_model.name,
            status=Product.Status(product_model.status),
            deleted=product_model.deleted,
        ).save(commit=False)
    db.session.commit()
    log(log.DEBUG, "[GET products from file] Done!")


def get_reseller_products():
    reseller_products = read_json("reseller_products")
    log(
        log.DEBUG,
        "[GET reseller products from file] Got [%d] products!",
        len(reseller_products),
    )
    for reseller_product in reseller_products:
        reseller_product_model: ResellerProductModel = ResellerProductModel.parse_obj(
            reseller_product
        )
        reseller = Reseller.query.filter(
            Reseller.name == reseller_product_model.reseller.name
        ).first()
        assert reseller
        product = Product.query.filter(
            Product.name == reseller_product_model.product.name
        ).first()
        assert product
        ResellerProduct(
            product_id=product.id,
            reseller_id=reseller.id,
            months=reseller_product_model.months,
            init_price=reseller_product_model.init_price,
            ext_price=reseller_product_model.ext_price,
        ).save(commit=False)
    db.session.commit()
    log(log.DEBUG, "[GET products from file] Done!")


def get_accounts():
    accounts = read_json("accounts")
    log(log.DEBUG, "[GET accounts from file] Got [%d] accounts!", len(accounts))
    for account in accounts:
        account_model: AccountModel = AccountModel.parse_obj(account)
        reseller = Reseller.query.filter(
            Reseller.name == account_model.reseller.name
        ).first()
        assert reseller
        product = Product.query.filter(
            Product.name == account_model.product.name
        ).first()
        assert product
        phone = Phone.query.filter(Phone.name == account_model.phone.name).first()
        assert phone
        Account(
            name=account_model.name[:60],
            product_id=product.id,
            phone_id=phone.id,
            reseller_id=reseller.id,
            sim=account_model.sim,
            imei=account_model.imei,
            comment=account_model.comment,
            activation_date=account_model.activation_date,
            months=account_model.months,
        ).save(commit=False)
    db.session.commit()
    log(log.DEBUG, "[GET accounts from file] Done!")


def get_account_ext():
    account_ext = read_json("accounts_ext")
    log(
        log.DEBUG,
        "[GET account extension from file] Got [%d] accounts!",
        len(account_ext),
    )
    for acc_ext in account_ext:
        acc_ext_model: AccountExtensionModel = AccountExtensionModel.parse_obj(acc_ext)
        if not acc_ext_model.account:
            log(log.WARNING, "[get_account_ext] no such account")
            continue
        reseller = Reseller.query.filter(
            Reseller.name == acc_ext_model.reseller.name
        ).first()
        assert reseller
        product = Product.query.filter(
            Product.name == acc_ext_model.product.name
        ).first()
        assert product
        account = Account.query.filter(
            Account.name == acc_ext_model.account.name,
        ).first()
        assert account
        AccountExtension(
            product_id=product.id,
            reseller_id=reseller.id,
            months=acc_ext_model.months,
            account_id=account.id,
            extension_date=acc_ext_model.extension_date,
            end_date=acc_ext_model.end_date,
        ).save(commit=False)
    db.session.commit()
    log(log.DEBUG, "[GET account extensions from file] Done!")


def get_accounts_changes():
    accounts_changes = read_json("accounts_changes")
    log(
        log.DEBUG,
        "[GET accounts_changes from file] Got [%d] changes!",
        len(accounts_changes),
    )
    for change in accounts_changes:
        change: AccountChangesModel = AccountChangesModel.parse_obj(change)
        if not change.account:
            # log(log.WARNING, "[get_accounts_changes] no such account")
            continue
        account = Account.query.filter(
            Account.name == change.account.name[:60],
        ).first()
        assert account
        user = User.query.filter(User.name == change.user.name).first()
        assert user
        HistoryChange(
            item_id=account.id,
            user_id=user.id,
            date=change.date,
            change_type=HistoryChange.EditType.changes_account,
            value_name=change.change_type.lower(),
            before_value_str=change.value_str if change.value_str else "[Empty]",
            after_value_str=change.new_value_str if change.new_value_str else "[Empty]",
            synced=True,
        ).save(commit=False)
    db.session.commit()
    log(log.DEBUG, "[GET accounts_changes from file] Done!")
