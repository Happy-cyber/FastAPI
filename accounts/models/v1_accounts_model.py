from pydantic import BaseModel, EmailStr, model_validator
from enum import Enum
from bson import ObjectId

from config.database import db
from config.renderer import CustomError


class DeviceType(str, Enum):
    ios = "I"
    android = "A"


class LoginType(str, Enum):
    email = "E"
    phone = "P"
    simple = "S"
    facebook = "F"
    google = "G"
    apple = "A"


class CreateUser(BaseModel):
    username: str
    email: EmailStr
    country_code: str
    phone_number: str
    password: str = ""
    login_type: LoginType
    social_key: str = ""

    @model_validator(mode='before')
    def validator(self):
        collection = db.get_collection("User")
        if not self.get('username', None):
            raise CustomError(message="Username field is required.")
        elif collection.find_one({"username": self['username']}):
            raise CustomError(message="This username already exists.")
        elif not self.get('email', None):
            raise CustomError(message="Email field is required.")
        elif collection.find_one({"email": self['email']}):
            raise CustomError(message="This email already exists.")
        elif not self.get('country_code', None) or not self.get('phone_number', None):
            raise CustomError(message="Both country_code and phone_number fields are required.")
        elif collection.find_one({"country_code": self['country_code'], "phone_number": self['phone_number']}):
            raise CustomError(message="This phone number already exists.")
        elif not self.get("login_type", None):
            raise CustomError(message="Login type field may not be blank.")
        elif self["login_type"] == "S" and not self.get('password', None):
            raise CustomError(message="Password field may not be blank.")
        elif self["login_type"] in ["A", "F", "G"] and not self.get('social_key', None):
            raise CustomError(message="Social key field may not be blank.")
        return self


class CreateToken(BaseModel):
    device_type: DeviceType
    device_token: str
    os_version: str = ""
    device_name: str = ""
    models_name: str = ""
    ip_address: str = ""
    uuid_number: str = ""
    imei_number: str = ""
    app_version: str
    api_version: str
    ios_device_token: str = ""

    @model_validator(mode='before')
    def validator(self):
        if not self.get("device_type", None):
            raise CustomError(message="Device type field may not be blank.")
        elif not self.get("device_token", None):
            raise CustomError(message="Device token field may not be blank.")
        elif not self.get("app_version", None):
            raise CustomError(message="APP version field may not be blank.")
        elif not self.get("api_version", None):
            raise CustomError(message="API version field may not be blank.")
        return self


class LoginUser(BaseModel):
    email: EmailStr = ""
    country_code: str = ""
    phone_number: str = ""
    password: str = ""
    login_type: LoginType
    social_key: str = ""
    device_type: DeviceType
    device_token: str
    os_version: str = ""
    device_name: str = ""
    models_name: str = ""
    ip_address: str = ""
    uuid_number: str = ""
    imei_number: str = ""
    app_version: str
    api_version: str
    ios_device_token: str = ""
    user_id: str = ""

    @model_validator(mode='before')
    def validator(self):
        collection = db.get_collection("User")
        if not self.get("login_type", None):
            raise CustomError(message="Login type field may not be blank.")
        elif not self.get("device_type", None):
            raise CustomError(message="Device type field may not be blank.")
        elif not self.get("device_token", None):
            raise CustomError(message="Device token field may not be blank.")
        elif not self.get("app_version", None):
            raise CustomError(message="APP version field may not be blank.")
        elif not self.get("api_version", None):
            raise CustomError(message="API version field may not be blank.")

        if self['login_type'] == "E":
            if not self.get("email", None):
                raise CustomError(message="Email field may not be blank")
            elif not self.get("password", None):
                raise CustomError(message="Password field may not be blank")

            user_obj = collection.find_one({"email": self['email'], "password": self['password']})
            if not user_obj:
                raise CustomError(message="Email and password do not match our database. Please try again.")
        elif self['login_type'] == "P":
            if not self.get('country_code', None) or not self.get('phone_number', None):
                raise CustomError(message="Both country_code and phone_number fields are required.")
            elif not self.get("password", None):
                raise CustomError(message="Password field may not be blank")

            user_obj = collection.find_one({
                "country_code": self['country_code'], "phone_number": self['phone_number'],
                "password": self['password']})
            if not user_obj:
                raise CustomError(message="Phone number and password do not match our database. Please try again.")
        elif self['login_type'] in ["F", "G", "A"]:
            if not self.get("social_key", None):
                raise CustomError(message="Social key field may not be blank")

            user_obj = collection.find_one({"login_type": self['login_type'], "social_key": self['social_key']})
            if not user_obj:
                raise CustomError(message="User not register.", code=12)
        else:
            raise CustomError(message="Login type not match.")

        if not user_obj.get("is_active", False):
            raise CustomError(
                message="Your account has been deactivated. Please contact the administrator for further assistance.")

        # Update self
        self['user_id'] = str(user_obj.get("_id"))
        return self


class Logout(BaseModel):
    is_sign_out_all: bool


class GetUserDetails(BaseModel):
    _id: str
    username: str
    email: EmailStr
    country_code: str
    phone_number: str
    login_type: str
    is_active: bool
    created_at: str
    token: str

    @classmethod
    def get_user(cls, user_id: str, token: str):
        user_data = db.get_collection("User").find_one({"_id": ObjectId(user_id)})
        if user_data:
            user_data['_id'] = str(user_data['_id'])
            user_data.update({"token": token})
            return cls(**user_data)
        else:
            return None
