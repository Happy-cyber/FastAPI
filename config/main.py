# ----------------------------------------------------------------------------------------------------------------------
# Import
import environ
import uvicorn

from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from config.renderer import CustomError
from config.utils import verify_api_key

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
app.include_router(v1_accounts_view.router, prefix="/api/v1", dependencies=[Depends(verify_api_key)])
app.include_router(v1_post_view.router, prefix="/api/v1", dependencies=[Depends(verify_api_key)])


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
# Run main thread using uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host=env('HOST'), port=int(env('PORT')))
