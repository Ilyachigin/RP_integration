from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any


class InnerParams(BaseModel):
    card: Optional[Dict[str, Any]]
    customer: Optional[Dict[str, Any]]
    extra_return_param: Optional[str] = None
    order_number: Optional[str] = None


class PaymentInfo(BaseModel):
    token: str
    gateway_amount: int
    gateway_currency: str


class PayoutRequest(BaseModel):
    params: InnerParams
    payment: PaymentInfo
    settings: Optional[Dict[str, Any]]
    processing_url: Optional[HttpUrl]
    callback_url: Optional[HttpUrl]
    method_name: Optional[str]
