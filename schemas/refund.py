from pydantic import BaseModel
from typing import Optional, Dict, Any


class InnerParams(BaseModel):
    amount: int


class PaymentInfo(BaseModel):
    amount: int
    gateway_token: str


class RefundRequest(BaseModel):
    params: InnerParams
    payment: PaymentInfo
    settings: Optional[Dict[str, Any]]
    method_name: Optional[str]
