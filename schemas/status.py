from pydantic import BaseModel
from typing import Optional, Dict, Any


class StatusParams(BaseModel):
    gateway_token: str

class GatewayStatus(BaseModel):
    settings: Optional[Dict[str, Any]]
    params: Optional[Dict[str, Any]]
    payment: StatusParams
    method_name: str

