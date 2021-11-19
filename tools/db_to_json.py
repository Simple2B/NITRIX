from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import json
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

DB_MIGRATION_DIR = "data-migrations/"


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

    users = User.query.filter(User.deleted == False).all()  # noqa E712
    log(log.DEBUG, "[GET users from db]Got [%d] users!", len(users))
    user_list: list[UserModel] = []
    for user in users:
        user: User = user
        if user.name != "admin":
            new_user = UserModel.from_orm(user)
            user_list.append(new_user.dict())

    with open(DB_MIGRATION_DIR + "user_list.json", "w", encoding="utf-8") as f:
        json.dump(user_list, f, ensure_ascii=False)
    log(log.DEBUG, "[GET users from db] Finished !")


def get_resellers():

    resellers = Reseller.query.filter(Reseller.deleted == False).all()  # noqa E712

    resellers_list: list[ResellerModel] = []
    log(log.DEBUG, "[GET resellers from db]Got [%s] resellers!", len(resellers))

    for reseller in resellers:
        reseller: Reseller = reseller
        if reseller.name != "NITRIX":
            new_reseller = ResellerModel.from_orm(reseller)
            resellers_list.append(new_reseller.dict())

    with open(DB_MIGRATION_DIR + "resellers_list.json", "w", encoding="utf-8") as f:
        json.dump(resellers_list, f, ensure_ascii=False)
    log(log.DEBUG, "[GET resellers from db] Finished !")


def get_reseller_products():

    reseller_products = ResellerProduct.query.all()

    reseller_products_list: list[ResellerProductModel] = []
    log(
        log.DEBUG,
        "[GET reseller_products from db]Got [%s] reseller_products!",
        len(reseller_products),
    )

    for res_prod in reseller_products:
        res_prod: ResellerProduct = res_prod
        new_res_prod = ResellerProductModel.from_orm(res_prod)
        reseller_products_list.append(new_res_prod.dict())

    with open(
        DB_MIGRATION_DIR + "reseller_products_list.json", "w", encoding="utf-8"
    ) as f:
        json.dump(reseller_products_list, f, ensure_ascii=False)
        log(log.DEBUG, "[GET reseller_products from db] Finished !")


def get_products():

    products = Product.query.filter(Product.deleted == False).all()  # noqa E712
    products_list: list[ProductModel] = []
    log(log.DEBUG, "[GET products from db]Got [%s] products!", len(products))

    for product in products:
        product: Product = product
        new_product = ProductModel.from_orm(product)
        products_list.append(new_product.dict())

    with open(DB_MIGRATION_DIR + "products_list.json", "w", encoding="utf-8") as f:
        json.dump(products_list, f, ensure_ascii=False)

    log(log.DEBUG, "[GET products from db] Finished !")


def get_phones():

    phones = Phone.query.filter(Phone.deleted == False).all()  # noqa E712

    log(log.DEBUG, "[GET phones from db]Got [%s] phones!", len(phones))
    phones_list: list[PhoneModel] = []

    for phone in phones:
        phone: Phone = phone
        if phone.name != "None":
            new_phone = PhoneModel.from_orm(phone)
            phones_list.append(new_phone.dict())

    with open(DB_MIGRATION_DIR + "phone_list.json", "w", encoding="utf-8") as f:
        json.dump(phones_list, f, ensure_ascii=False)
    log(log.DEBUG, "[GET phones from db] Finished !")


def get_accounts():

    accounts = Account.query.filter(Account.deleted == False).all()  # noqa E712
    log(log.DEBUG, "[GET accounts from db] Got [%s] accounts!", len(accounts))

    accounts_list: list[AccountModel] = []

    for account in accounts:
        new_account = AccountModel.from_orm(account)
        accounts_list.append(new_account.json())

    with open(DB_MIGRATION_DIR + "accounts_list.json", "w", encoding="utf-8") as f:
        json.dump(accounts_list, f, ensure_ascii=False)
    log(log.DEBUG, "[GET accounts from db] Finished !")


def get_account_ext():

    accounts_ext = AccountExtension.query.all()
    log(
        log.DEBUG, "[GET accounts_ext from db]Got [%s] accounts_ext!", len(accounts_ext)
    )

    accounts_ext_list: list[AccountExtensionModel] = []

    for acc_ext in accounts_ext:
        new_acc_ext = AccountExtensionModel.from_orm(acc_ext)
        accounts_ext_list.append(new_acc_ext.json())

    with open(DB_MIGRATION_DIR + "accounts_ext_list.json", "w", encoding="utf-8") as f:
        json.dump(accounts_ext_list, f, ensure_ascii=False)
    log(log.DEBUG, "[GET accounts_ext from db] Finished !")


def get_account_changes():

    accounts_changes = AccountChanges.query.all()
    log(
        log.DEBUG,
        "[GET accounts_changes from db]Got [%s] accounts_changes!",
        len(accounts_changes),
    )

    accounts_changes_list: list[AccountChangesModel] = []

    for acc_change in accounts_changes:
        new_acc_ext = AccountChangesModel.from_orm(acc_change)
        accounts_changes_list.append(new_acc_ext.json())

    with open(
        DB_MIGRATION_DIR + "accounts_changes_list.json", "w", encoding="utf-8"
    ) as f:
        json.dump(accounts_changes_list, f, ensure_ascii=False)
    log(log.DEBUG, "[GET accounts_changes from db] Finished !")
