import datetime
import binascii
import os
import environ
from fastapi import Header, Request

from config.database import db
from config.renderer import CustomError

# ----------------------------------------------------------------------------------------------------------------------
# Initial environment instance
env = environ.Env()
environ.Env.read_env()


# Get current UTC datetime
def get_current_datetime():
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def generate_token():
    return binascii.hexlify(os.urandom(20)).decode()


async def verify_api_key(api_key: str = Header(None)):
    if not api_key:
        raise CustomError(message="API authentication credentials were not provided.")

    if api_key != env('API_KEY'):
        # Return a 403 Forbidden response if the API key is invalid
        raise CustomError(message="Invalid API key.", status_code=403)


async def verify_token(request: Request, Authorization: str = Header(None)):
    if not Authorization:
        raise CustomError(message="User authentication credentials were not provided.")
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
