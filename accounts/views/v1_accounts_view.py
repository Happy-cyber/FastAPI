from fastapi import APIRouter, Depends, Request
from bson import ObjectId

from config.database import db
from config.renderer import CustomizeResponse
from accounts.models.v1_accounts_model import CreateUser, CreateToken, GetUserDetails, LoginUser, Logout
from config.utils import get_current_datetime, generate_token, verify_token


router = APIRouter(prefix="/auth")


@router.post("/create-user/")
async def create_user(user_body: CreateUser, token_body: CreateToken):
    current_datetime = get_current_datetime()

    # User Body
    user_body = user_body.dict()
    user_body['is_active'] = True
    user_body['created_at'] = current_datetime
    user_body['updated_at'] = current_datetime
    user_body['deleted_at'] = current_datetime

    # Token Body
    token_body = token_body.dict()
    token_body['is_active'] = True
    token_body['created_at'] = current_datetime

    # Get collection
    user_collection = db.get_collection("User")
    token_collection = db.get_collection("Token")

    # Insert document
    user_obj = user_collection.insert_one(user_body)

    # Insert token document
    token_body['user_id'] = user_obj.inserted_id
    token_body['token'] = generate_token()
    token_collection.insert_one(token_body)

    # Fetch inserted document
    data = GetUserDetails.get_user(user_obj.inserted_id, token_body['token']).dict()

    return CustomizeResponse(code=1, message="Document created successfully.", data=data)


@router.post("/login/")
async def login(login_body: LoginUser):
    # Login body
    login_body = login_body.dict()
    login_body['is_active'] = True
    login_body['user_id'] = ObjectId(login_body['user_id'])
    login_body['token'] = generate_token()

    # Pop others keys
    login_body.pop("email")
    login_body.pop("country_code")
    login_body.pop("phone_number")
    login_body.pop("password")
    login_body.pop("login_type")
    login_body.pop("social_key")

    # Get collection
    token_collection = db.get_collection("Token")

    # Insert token document
    token_collection.insert_one(login_body)

    # Fetch inserted document
    data = GetUserDetails.get_user((login_body['user_id']), login_body['token']).dict()
    return CustomizeResponse(code=1, message="User login successfully.", data=data)


@router.post("/logout/", dependencies=[Depends(verify_token)])
async def logout(logout_body: Logout, request: Request):
    is_sign_out_all = logout_body.is_sign_out_all

    # Get collection
    collection = db.get_collection("Token")
    token = request.headers.get("Authorization").split()[1]

    if is_sign_out_all:
        result = collection.find_one({"token": token}, {"user_id": 1})
        if result:
            user_id = result["user_id"]
            # Delete all entries related to the found user_id
            collection.delete_many({"user_id": user_id})
    else:
        collection.delete_one({"token": token})

    return CustomizeResponse(code=1, message="Logout successfully.")
