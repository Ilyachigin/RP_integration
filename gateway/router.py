from fastapi import APIRouter

from schemas.payment import PaymentRequest
from schemas.payout import PayoutRequest
from schemas.refund import RefundRequest
from schemas.status import GatewayStatus
from schemas.callback import GatewayCallback
from gateway.handler import (
    handle_pay,
    handle_status,
    handle_callback,
    handle_refund,
    handle_payout
)

router = APIRouter()


@router.post("/pay")
async def pay(data: PaymentRequest):
    return await handle_pay(data)


@router.post("/payout")
async def pay(data: PayoutRequest):
    return await handle_payout(data)


@router.post("/refund")
async def pay(data: RefundRequest):
    return await handle_refund(data)


@router.post("/status")
async def status(data: GatewayStatus):
    return await handle_status(data)


@router.post("/callback")
async def callback(data: GatewayCallback):
    return await handle_callback(data)

