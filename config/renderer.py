from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from main import app


class CustomError(ValueError):
    def __init__(self, message, code=0, status_code=200):
        self.code = code
        self.status_code = status_code
        super().__init__(message)


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


def CustomizeResponse(code=1, message="Success", data=None, status_code=200):
    response = {
        "code": code,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return JSONResponse(status_code=status_code, content=response)
