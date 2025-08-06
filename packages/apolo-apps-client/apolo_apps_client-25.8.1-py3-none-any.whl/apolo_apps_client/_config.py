from pydantic import BaseModel


class AppsClientConfig(BaseModel):
    url: str
    token: str | None = None
