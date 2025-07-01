import jwt
import base64
import hashlib
from fastapi import Response
from fastapi.encoders import jsonable_encoder
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

import config
from client.http import send_request
from utils.db import DatabaseStorage
from schemas.payment import GatewayRequest
from schemas.callback import GatewayCallback
from schemas.status import GatewayStatus
from utils.logger import logger

from gateway.builder import (
    gateway_body,
    gateway_status_param,
    gateway_pay_response,
    gateway_status_response,
    gateway_callback_body,
)

db = DatabaseStorage()


async def handle_pay(data: GatewayRequest):
    url = f"{config.GATEWAY_URL}/api/v1/payments"
    raw_data = data.model_dump(exclude_none=True)
    gateway_payload = gateway_body(raw_data)
    bearer_token = raw_data.get("settings").get("bearer_token")
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    response = send_request('POST', url, headers, jsonable_encoder(gateway_payload))
    database_insert(response.get('response'), bearer_token)

    return response_handler('pay', response, url, gateway_payload, response['duration'])


async def handle_status(data: GatewayStatus):
    raw_data = data.model_dump(exclude_none=True)
    gateway_token = gateway_status_param(raw_data)
    url = f"{config.GATEWAY_URL}/api/v1/payments/{gateway_token}"

    bearer_token = raw_data.get("settings").get("bearer_token")
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    response = send_request('GET', url, headers, gateway_token)
    return response_handler('status', response, url, gateway_token, response['duration'])


async def handle_callback(data: GatewayCallback):
    raw_data = data.model_dump(exclude_none=True)
    bearer_token = db.get_token(raw_data.get("token"))

    signature = callback_signature(raw_data, bearer_token)
    if signature == raw_data.get("signature"):
        gateway_token, callback_body = gateway_callback_body(raw_data)

        secure_data = merchant_token_encrypt(bearer_token, config.SIGN_KEY)
        jwt_payload = {
            **callback_body,
            "secure": secure_data}

        # TEMP
        logger.info(f"JWT body: {jwt_payload}")

        jwt_token = callback_jwt(jwt_payload, config.SIGN_KEY)

        callback_headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

        # Temp
        logger.info(f"Callback headers: {callback_headers}")

        # Temp
        logger.info(f"Callback body: {callback_body}")

        url = f"{config.BUSINESS_URL}/callbacks/v2/gateway_callbacks/{gateway_token}"
        send_request('POST', url, callback_headers, callback_body)
    return Response(content="ok", status_code=200)


def callback_signature(data, bearer_token):
    params = ["token", "type", "status", "extraReturnParam",
              "orderNumber", "amount", "currency", "gatewayAmount", "gatewayCurrency"]
    signature_string = ''

    for value in params:
        if data[value] in [None, ""]:
            continue
        str_len = str(len(str(data[value])))
        signature_string += str_len + str(data[value])

    signature_string = signature_string + bearer_token
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

def database_insert(data, bearer_token):
    token = data.get("token")
    if token:
        db.insert_token(token, bearer_token)
        db.delete_old_tokens()

