def success_response(message, data=None, status_code=200):
    return {
        "status": "success",
        "message": message,
        "status_code": status_code,
        "data": data or []
    }


def error_response(message, status_code=400):
    return {
        "status": "failed",
        "message": message,
        "status_code": status_code,
        "data": []
    }