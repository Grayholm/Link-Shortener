class AppError(Exception):
    detail = "An error occurred"
    status_code = 400


class LinkNotFoundError(AppError):
    detail = "Link not found"
    status_code = 404


class IsNotDoneToCreateUniqueLinkError(AppError):
    detail = "Unable to create a unique link after multiple attempts"
    status_code = 409
