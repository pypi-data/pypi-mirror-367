from datetime import datetime

from pydantic import BaseModel


class AppInstance(BaseModel):
    id: str
    name: str
    creator: str
    cluster_name: str
    org_name: str
    project_name: str
    namespace: str
    created_at: datetime
