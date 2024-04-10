from fastapi import Depends, Request

from config.main import router_v1
from config.renderer import CustomizeResponse
from config.utils import verify_token, get_current_datetime
from post.models.v1_post_model import CreatePost
from config.database import db


@router_v1.post("/post/create/", dependencies=[Depends(verify_token)])
async def create_post(post_body: CreatePost, request: Request):
    current_datetime = get_current_datetime()

    user = request['state']['user']

    # Post Body
    post_body = post_body.dict()
    post_body['is_active'] = True
    post_body['created_at'] = current_datetime
    post_body['updated_at'] = current_datetime
    post_body['deleted_at'] = current_datetime

    # Get collection
    post_collection = db.get_collection("Post")

    # Insert post document
    post_obj = post_collection.insert_one(post_body)

    return CustomizeResponse(code=1, message="Post created successfully.", data=None)
