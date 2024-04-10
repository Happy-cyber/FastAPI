# ----------------------------------------------------------------------------------------------------------------------
# Import
import environ
import uvicorn

from fastapi import FastAPI, APIRouter

# ----------------------------------------------------------------------------------------------------------------------
# Initial environment instance
env = environ.Env()
environ.Env.read_env()

# ----------------------------------------------------------------------------------------------------------------------
# Initial fastAPI instance
app = FastAPI()

# ----------------------------------------------------------------------------------------------------------------------
# Define API routers for different versions
router_v1 = APIRouter(prefix="/api/v1")

# ----------------------------------------------------------------------------------------------------------------------
# Import all API views
from post.views.v1_post_view import *
from accounts.views.v1_accounts_view import *

# ----------------------------------------------------------------------------------------------------------------------
# Import render class
from renderer import *

# ----------------------------------------------------------------------------------------------------------------------
# Include routers in the main app
app.include_router(router_v1)


# ----------------------------------------------------------------------------------------------------------------------
# Define a middleware function to check the API key
async def api_key_middleware(request: Request, call_next: callable):
    api_key = request.headers.get("API-Key")

    if api_key != env('API_KEY'):
        # Return a 403 Forbidden response if the API key is invalid
        return CustomizeResponse(code=0, message="Invalid API key.", status_code=403)

    # Call the next middleware or route handler
    response = await call_next(request)
    return response


# Register the middleware with the FastAPI app
app.middleware("http")(api_key_middleware)

# ----------------------------------------------------------------------------------------------------------------------
# Run main thread using uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host=env('HOST'), port=int(env('PORT')))
