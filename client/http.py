import time
import requests

from utils.logger import logger


def send_request(method: str, url: str, headers: dict, payload: dict | str) -> dict:
    start_time = time.perf_counter()

    logger.info(f"Gateway request URL: {url}")
    logger.info(f"Gateway request params: {payload}")

    try:
        if method == "POST":
            response = requests.post(url, headers=headers, json=payload)
        else:
            response = requests.get(url, headers=headers)
        logger.info(f"Gateway response: {response.text}")

        response.raise_for_status()
        result = {
            "status": "ok",
            "status_code": response.status_code,
            "response": response.json()
        }
    except requests.exceptions.HTTPError as http_err:
        result = {
            "status": "error",
            "error": f"HTTP error: {str(http_err)}",
            "status_code": getattr(http_err.response, "status_code", None),
            "body": getattr(http_err.response, "text", None)
        }
    except requests.exceptions.RequestException as e:
        result = {
            "status": "error",
            "error": f"Request error: {str(e)}"
        }
    result["duration"] = round(time.perf_counter() - start_time, 4)
    return result

