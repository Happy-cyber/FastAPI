from typing import List
from pydantic import BaseModel, model_validator
from enum import Enum
from config.renderer import CustomError


class ImageTypes(str, Enum):
    dusk = "Dusk"
    none = "Noon"
    dawn = "Dawn"
    dual = "Dual"


class PostTypes(str, Enum):
    normal = "Normal"
    advertisement = "Advertisement"


class MediaType(str, Enum):
    image = "Image"
    video = "Video"


class MediaItem(BaseModel):
    url: str
    type: MediaType
    thumb: str = ""
    height: str = "100"
    width: str = "100"

    @model_validator(mode='before')
    def validator(self):
        if not self.get('url', None):
            raise CustomError(message="Url field may not be blank.")
        elif not self.get('type', None):
            raise CustomError(message="Type field may not be blank.")
        return self


class CreatePost(BaseModel):
    description: str
    location_name: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    image_type: ImageTypes
    post_type: PostTypes
    is_close_friend_post: bool
    media: List[MediaItem]

    @model_validator(mode='before')
    def validator(self):
        if not self.get('description', None):
            raise CustomError(message="Description field may not be blank.")
        elif not self.get('media', None):
            raise CustomError(message="Media field may not be blank.")
        return self
