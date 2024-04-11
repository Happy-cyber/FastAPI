# ----------------------------------------------------------------------------------------------------------------------
# Import
import environ
import uvicorn

from fastapi import FastAPI
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from config.renderer import CustomError, CustomizeResponse
from starlette.responses import JSONResponse

from accounts.views import v1_accounts_view
from post.views import v1_post_view

# ----------------------------------------------------------------------------------------------------------------------
# Initial environment instance
env = environ.Env()
environ.Env.read_env()

# ----------------------------------------------------------------------------------------------------------------------
# Initial fastAPI instance
app = FastAPI()

# ----------------------------------------------------------------------------------------------------------------------
# Define API routers for different versions
app.include_router(v1_accounts_view.router, prefix="/api/v1")
app.include_router(v1_post_view.router, prefix="/api/v1")


# ----------------------------------------------------------------------------------------------------------------------
# Create custom error handler async function
@app.exception_handler(CustomError)
@app.exception_handler(RequestValidationError)
async def custom_error_handler(request: Request, exc):
    if isinstance(exc, CustomError):
        code = exc.code
        status_code = exc.status_code
        message = exc.args[0]
    elif isinstance(exc, RequestValidationError):
        try:
            code = exc.args[0][0]['ctx']['error'].code
        except:
            code = 0

        try:
            status_code = exc.args[0][0]['ctx']['error'].status_code
        except:
            status_code = 200

        try:
            message = exc.args[0][0]['ctx']['error'].args[0]
        except:
            message = f"{exc.args[0][0]['loc'][1]} : {exc.args[0][0]['type']} : {exc.args[0][0]['msg']}"
    else:
        code = -51
        message = "Something went wrong into Custom Error Handler"
        status_code = 200

    data = {
        "code": code,
        "message": message
    }
    return JSONResponse(status_code=status_code, content=data)


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
