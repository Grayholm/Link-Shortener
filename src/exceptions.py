class AppError(Exception):
    detail = "An error occurred"
    status_code = 400

class LinkNotFoundError(AppError):
    detail = "Link not found"
    status_code = 404

class LinkAlreadyExistsError(AppError):
    detail = "Link already exists"
    status_code = 409
