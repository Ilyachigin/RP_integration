from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional, Dict, Any


class BrowserInfo(BaseModel):
    tz_name : Optional[str] = None
    accept_header: Optional[str] = None
    color_depth: Optional[str] = None
    ip: Optional[str] = None
    language: Optional[str] = None
    screen_height: Optional[str] = None
    screen_width: Optional[str] = None
    tz: Optional[str] = None
    user_agent: Optional[str] = None
    java_enabled: Optional[str] = None
    window_width: Optional[str] = None
    window_height: Optional[str] = None


class InnerParams(BaseModel):
    pan: str
    expires: str
    holder: str
    cvv: str
    email: str
    extra_return_param: Optional[str] = None
    order_number: Optional[str] = None
    product: Optional[str]
    ip: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
    browser: Optional[BrowserInfo] = None


class PaymentInfo(BaseModel):
    token: str
    gateway_amount: int
    gateway_currency: str
    redirect_success_url: HttpUrl
    redirect_fail_url: HttpUrl


class ParamsBlock(BaseModel):
    settings: Optional[Dict[str, Any]]
    params: Optional[InnerParams]


class GatewayRequest(BaseModel):
    params: ParamsBlock
    payment: PaymentInfo
    processing_url: Optional[HttpUrl]
    callback_url: Optional[HttpUrl]
    callback_3ds_url: Optional[HttpUrl]
    method_name: Optional[str]


class PaymentStatus(BaseModel):
    gateway_token: str


class StatusRequest(BaseModel):
    settings: str
    params: Optional[Dict[str, Any]]
    payment: PaymentStatus
    method_name: str


class GatewayCallback(BaseModel):
    model_config = ConfigDict(extra='allow')
    token: str
    status: str
    type: str
    signature: str
