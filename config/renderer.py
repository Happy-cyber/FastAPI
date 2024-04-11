from starlette.responses import JSONResponse


class CustomError(ValueError):
    def __init__(self, message, code=0, status_code=200):
        self.code = code
        self.status_code = status_code
        super().__init__(message)


def CustomizeResponse(code=1, message="Success", data=None, status_code=200):
    response = {
        "code": code,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return JSONResponse(status_code=status_code, content=response)
