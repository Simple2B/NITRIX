from datetime import datetime
import json
from app.models import User, Reseller

# , ResellerProduct, Phone
from pydantic import BaseModel


def get_users():
    class UserModel(BaseModel):
        name: str
        user_type: User.Type
        password_hash: str
        activated: User.Status
        otp_secret: str
        otp_active: bool

        class Config:
            orm_mode = True

    users = User.query.all()

    user_list: list[UserModel] = []
    for user in users:
        user: User = user
        if user.name != "admin" or not user.deleted:
            new_user = UserModel.from_orm(user)
            # new_user = DbUser
            # new_user.name = user.name
            # new_user.user_type = user.user_type
            # new_user.password_hash = user.password_hash
            # new_user.activated = user.activated
            # new_user.deleted = user.deleted
            # new_user.otp_secret = user.otp_secret
            # new_user.otp_active = user.otp_active
            user_list.append(new_user)

    with open("user_list.json", "w", encoding="utf-8") as f:
        json.dump(user_list, f, ensure_ascii=False)
    # return json.dumps(user_list)


# with open('data.json', 'w', encoding='utf-8') as f:
#     json.dump(data, f, ensure_ascii=False, indent=4)


def get_resellers():
    class ResellerModel(BaseModel):
        name: str
        status: Reseller.Status
        comments: str
        deleted: bool
        last_activity: datetime
        ninja_client_id: str

    resellers = Reseller.query.all()

    resellers_list: list[ResellerModel] = []
    for reseller in resellers:
        reseller: Reseller = reseller
        new_reseller = ResellerModel
        new_reseller.name = reseller.name
        new_reseller.status = reseller.status
        new_reseller.comments = reseller.comments
        new_reseller.deleted = reseller.deleted
        new_reseller.last_activity = reseller.last_activity
        new_reseller.ninja_client_id = reseller.ninja_client_id

        resellers_list.append(new_reseller)

    return json.dumps(resellers_list)
