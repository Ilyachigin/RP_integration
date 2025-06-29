from gateway.handler import handle_pay, handle_status, handle_callback
from schemas.payment import GatewayRequest, StatusRequest, GatewayCallback

from fastapi import APIRouter

router = APIRouter()


@router.post("/pay")
async def pay(data: GatewayRequest):
    return await handle_pay(data)


@router.post("/status")
async def status(data: StatusRequest):
    return await handle_status(data)


@router.post("/callback")
async def callback(data: GatewayCallback):
    return await handle_callback(data)
