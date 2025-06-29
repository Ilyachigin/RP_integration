import jwt
import base64
import hashlib
from fastapi import Response
from fastapi.encoders import jsonable_encoder
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

import config
from client.http import send_request
from schemas.payment import GatewayRequest, StatusRequest, GatewayCallback
from gateway.builder import (
    gateway_body,
    gateway_status_param,
    gateway_pay_response,
    gateway_status_response,
    gateway_callback_body,
)

headers = {
    "Authorization": f"Bearer {config.BEARER_TOKEN}",
    "Content-Type": "application/json"
}


async def handle_pay(data: GatewayRequest):
    url = f"{config.GATEWAY_URL}/api/v1/payments"
    raw_data = data.model_dump(exclude_none=True)
    gateway_payload = gateway_body(raw_data)
    response = send_request('POST', url, headers, jsonable_encoder(gateway_payload))

    return response_handler('pay', response, url, gateway_payload, response['duration'])


async def handle_status(data: StatusRequest):
    raw_data = data.model_dump(exclude_none=True)
    gateway_token = gateway_status_param(raw_data)
    url = f"{config.GATEWAY_URL}/api/v1/payments/{gateway_token}"
    response = send_request('GET', url, headers, gateway_token)
    return response_handler('status', response, url, gateway_token, response['duration'])


async def handle_callback(data: GatewayCallback):
    raw_data = data.model_dump(exclude_none=True)

    signature = callback_signature(raw_data)
    if signature == raw_data.get("signature"):
        gateway_token, callback_body = gateway_callback_body(raw_data)

        secure_data = merchant_token_encrypt(config.BEARER_TOKEN, config.SIGN_KEY)
        jwt_payload = {
            **callback_body,
            "secure": secure_data}
        jwt_token = callback_jwt(jwt_payload, config.SIGN_KEY)

        callback_headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        url = f"{config.BUSINESS_URL}/callbacks/v2/gateway_callbacks/{gateway_token}"
        send_request('POST', url, callback_headers, gateway_token)
    return Response(content="ok", status_code=200)


def callback_signature(data):
    params = ["token", "type", "status", "extraReturnParam",
              "orderNumber", "amount", "currency", "gatewayAmount", "gatewayCurrency"]
    signature_string = ''

    for value in params:
        str_len = str(len(str(data[value])))
        signature_string += str_len + str(data[value])

    signature_string = signature_string + config.BEARER_TOKEN
    return hashlib.md5(signature_string.encode('utf-8')).hexdigest()


def callback_jwt(callback_body: dict, sign_key: str) -> str:
    return jwt.encode(
        payload=callback_body,
        key=sign_key,
        algorithm="HS512"
    )


def merchant_token_encrypt(merchant_token: str, sign_key: str) -> dict:
    def pad(data: bytes) -> bytes:
        pad_len = 16 - (len(data) % 16)
        return data + bytes([pad_len] * pad_len)

    key = sign_key.encode('utf-8')[:32]
    iv = get_random_bytes(16)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(merchant_token.encode('utf-8'))
    encrypted = cipher.encrypt(padded_data)

    return {
        "encrypted_data": base64.b64encode(encrypted).decode('utf-8'),
        "iv_value": base64.b64encode(iv).decode('utf-8')
    }


def response_handler(request_type, response, url, body, duration):
    if response["status"] == "ok":
        if request_type == "pay":
            return gateway_pay_response(response["response"], url, body, duration)
        elif request_type == "status":
            return gateway_status_response(response["response"], url, body, duration)
        return None
    else:
        return {
            "status": "error",
            "message": response["error"],
            "status_code": response.get("status_code")
        }
