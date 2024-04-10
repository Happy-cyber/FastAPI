import datetime
import binascii
import os
from typing import Annotated
from fastapi import Header, Request

from config.database import db
from config.renderer import CustomError


# Get current UTC datetime
def get_current_datetime():
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def generate_token():
    return binascii.hexlify(os.urandom(20)).decode()


async def verify_token(Authorization: Annotated[str, Header()], request: Request):
    if not Authorization:
        raise CustomError(message="Authentication credentials were not provided.")
    auth = Authorization.split()

    if len(auth) == 1:
        raise CustomError(message="Invalid token header. No credentials provided.")
    elif len(auth) > 2:
        raise CustomError(message="Invalid token header. Token string should not contain spaces.")

    key = auth[1]
    # Get collection
    collection = db.get_collection("Token")
    token_obj = collection.find_one({"token": key})
    if not token_obj:
        raise CustomError(message="Invalid token.")

    user_details = db.get_collection("User").find_one({"_id": token_obj.get("user_id")})

    if not user_details or not user_details.get("is_active", False):
        raise CustomError(
            message="Your account has been deactivated. Please contact the administrator for further assistance.")

    # Update Request state
    request['state']['user'] = user_details
