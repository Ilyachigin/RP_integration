from pydantic import BaseModel, ConfigDict


class GatewayCallback(BaseModel):
    model_config = ConfigDict(extra='allow')
    token: str
    status: str
    type: str
    signature: str
