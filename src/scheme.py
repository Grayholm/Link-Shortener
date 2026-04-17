from pydantic import BaseModel, HttpUrl


class ShortLinkRequest(BaseModel):
    long_url: HttpUrl
