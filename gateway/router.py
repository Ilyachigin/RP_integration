from gateway.handler import handle_pay, handle_status, handle_callback
from schemas.payment import GatewayRequest
from schemas.status import GatewayStatus
from schemas.callback import GatewayCallback

from fastapi import APIRouter

router = APIRouter()


@router.post("/pay")
async def pay(data: GatewayRequest):
    return await handle_pay(data)


@router.post("/status")
async def status(data: GatewayStatus):
    return await handle_status(data)


@router.post("/callback")
async def callback(data: GatewayCallback):
    return await handle_callback(data)
