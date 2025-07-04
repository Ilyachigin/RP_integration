from datetime import datetime
import copy

from typing import Dict, Any

import config


def gateway_body(business_data: Dict) -> Dict:
    main_dict = main_params(business_data)

    card = business_data.get("params")
    card_dict = card_params(card)

    customer = business_data.get("params")
    browser = customer.get("browser", {})
    customer_dict = customer_params(customer)
    browser_dict = browser_params(browser)
    customer_data = {**customer_dict}
    if browser_dict:
        customer_data["browser"] = browser_dict

    return {
        **main_dict,
        "card": card_dict,
        "customer": customer_data
    }


def browser_params(data: dict) -> Dict:
    params = {
        "tz_name": data.get("tz_name"),
        "accept_header": data.get("accept_header"),
        "color_depth": data.get("color_depth"),
        "ip": data.get("ip"),
        "language": data.get("language"),
        "screen_height": data.get("screen_height"),
        "screen_width": data.get("screen_width"),
        "tz": data.get("tz"),
        "user_agent": data.get("user_agent"),
        "java_enabled": data.get("java_enabled"),
        "window_width": data.get("window_width"),
        "window_height": data.get("window_height"),
    }
    return {k: v for k, v in params.items() if v is not None}


def customer_params(data: dict) -> Dict:
    params = {
        "ip": data.get("ip"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "country": data.get("country"),
        "state": data.get("state"),
        "postcode": data.get("postcode"),
        "city": data.get("city"),
        "address": data.get("address"),
    }
    return {k: v for k, v in params.items() if v is not None}


def main_params(data: dict) -> Dict:
    params = {
        "product": data.get("payment", {}).get("product"),
        "amount": data.get("payment", {}).get("gateway_amount"),
        "currency": data.get("payment", {}).get("gateway_currency"),
        "extra_return_param": data.get("params").get("extra_return_param"),
        "order_number": data.get("params").get("order_number"),
        "redirect_success_url": data.get("payment", {}).get("redirect_success_url"),
        "redirect_fail_url": data.get("payment", {}).get("redirect_fail_url"),
        "callback_url": f"{config.BASE_URL}/callback"
    }
    return {k: v for k, v in params.items() if v is not None}


def card_params(data: dict) -> Dict:
    params = {
        "pan": data.get("pan"),
        "expires": data.get("expires"),
        "holder": data.get("holder"),
        "cvv": data.get("cvv"),
    }
    return {k: v for k, v in params.items() if v is not None}


def response_redirect_params(redirect_request: dict, token: str) -> Dict:
    redirect_type = redirect_request.get("type", "post")
    redirect_url = redirect_request.get("url")
    redirect_data = redirect_request.get("params", {})

    return {
        "url": redirect_url,
        "type": "post_iframes" if redirect_type == "post" else redirect_type,
        "iframes": [
            {
                "url": redirect_url,
                "data": {
                    **redirect_data,
                    "token": token
                }
            }
        ]
    }


def response_logs_params(kind: str, request_url: str, request_data: dict, response: dict, duration: float) -> list:
    return [
        {
            "gateway": "ReactivePay",
            "request": {
                "url": request_url,
                "params": mask_data(request_data)
            },
            "status": response.get("status"),
            "response": str(response),
            "kind": kind,
            "created_at": datetime.now().isoformat(),
            "duration": duration
        }
    ]


def mask_data(data: dict) -> dict:
    masked = copy.deepcopy(data)

    if "card" in masked:
        masked["card"]["cvv"] = "***"

        pan = masked["card"].get("pan", "")
        if len(pan) >= 10:
            masked["card"]["pan"] = f"{pan[:6]}******{pan[-4:]}"
        else:
            masked["card"]["pan"] = "************"

    return masked


def gateway_status_param(data: dict) -> str:
    return data.get("payment").get("gateway_token")


def gateway_refund_body(data: dict) -> dict[str, Any]:
    refund_amount = data.get("params").get("amount")
    gateway_token = data.get("payment").get("gateway_token")

    return {
        "token": gateway_token,
        "amount": refund_amount
    }


def gateway_payout_body(business_data: dict) -> dict[str, Any]:
    main_dict = main_params(business_data)

    card = business_data.get("params").get("card")
    card_dict = card_params(card)

    customer = business_data.get("params").get("customer")
    customer_dict = customer_params(customer)
    customer_data = {**customer_dict}

    return {
        **main_dict,
        "card": card_dict,
        "customer": customer_data
    }


def gateway_callback_body(data: dict) -> tuple[str | None, dict[str, str | int]]:
    token = data.get("token")

    callback_body = {
        "status": data.get("status"),
        "currency": data.get("currency"),
        "amount": data.get("amount")
    }
    return token, callback_body


def gateway_pay_response(response: dict, request_url: str, request_data: dict, duration: float) -> Dict:
    token = response.get("token")

    processing_url = response.get("processingUrl")
    result = response.get("payment", {}).get("status")

    return {
        "status": "OK",
        "gateway_token": token,
        "result": result,
        "processing_url": processing_url,
        "redirect_request": response_redirect_params(response.get("redirectRequest", {}), token),
        "logs": response_logs_params('pay', request_url, request_data, response, duration)
    }


def gateway_status_response(response: dict, request_url: str, request_data: dict, duration: float):
    payment = response.get("payment", {})
    status = payment.get("status")
    amount = payment.get("amount")
    currency = payment.get("currency")

    if status == 'declined':
        details = payment.get("declination_reason")
    else:
        details = f'Transaction is {status}'
    return {
        "result": "OK",
        "status": status,
        "details": details,
        "amount": amount,
        "currency": currency,
        "logs": response_logs_params('status', request_url, request_data, response, duration)
    }
