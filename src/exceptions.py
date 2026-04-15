class AppError(Exception):
    detail = "An error occurred"

class LinkNotFoundError(AppError):
    detail = "Link not found"