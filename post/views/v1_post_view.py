from fastapi import APIRouter, Depends, Request

from config.renderer import CustomizeResponse
from config.utils import verify_token, get_current_datetime
from post.models.v1_post_model import CreatePost
from config.database import db


router = APIRouter(prefix="/post", dependencies=[Depends(verify_token)])


@router.post("/create/")
async def create_post(post_body: CreatePost, request: Request):
    current_datetime = get_current_datetime()

    # Get user details in request
    user = request['state']['user']

    # Post Body
    post_body = post_body.dict()
    post_body['is_active'] = True
    post_body['created_at'] = current_datetime
    post_body['updated_at'] = current_datetime
    post_body['deleted_at'] = current_datetime

    # Update media using map function with lambda and enumerate to update dictionaries
    post_body['media'] = list(
        map(
            lambda indexed_dict: {**indexed_dict[1], "id": indexed_dict[0] + 1},
            enumerate(post_body['media'])
        )
    )

    # Get collection
    post_collection = db.get_collection("Post")

    # Insert post document
    post_collection.insert_one(post_body)

    return CustomizeResponse(code=1, message="Post created successfully.", data=None)


@router.get("/list/")
async def post_list(request: Request):
    # Get collection
    post_collection = db.get_collection("Post")

    pipeline = [
        {
            "$addFields": {
                "_id": {
                    "$toString": "$_id"
                }
            }
        },
        {
            "$sort": {
                "created_at": -1
            }
        }
    ]

    data = list(post_collection.aggregate(pipeline))
    return CustomizeResponse(code=1, message="Post get successfully.", data=data)
