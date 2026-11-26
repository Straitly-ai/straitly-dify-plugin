from http import HTTPStatus

import requests
from dify_plugin.errors.model import CredentialsValidateFailedError

DEFAULT_ENDPOINT_URL = "https://api.straitly.ai/v1"
VALIDATION_TIMEOUT = (10, 30)


def resolve_endpoint_url(credentials: dict) -> str:
    raw = credentials.get("endpoint_url")
    if isinstance(raw, str) and raw.strip():
        return raw.strip().rstrip("/")
    return DEFAULT_ENDPOINT_URL


def _get(url: str, api_key: str) -> requests.Response:
    try:
        return requests.get(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            timeout=VALIDATION_TIMEOUT,
        )
    except requests.RequestException as ex:
        raise CredentialsValidateFailedError(
            "Unable to reach Straitly for credential validation"
        ) from ex


def validate_model_access(credentials: dict, model: str | None = None) -> None:
    api_key = credentials.get("api_key")
    if not isinstance(api_key, str) or not api_key.strip():
        raise CredentialsValidateFailedError("Straitly API key is required")
    api_key = api_key.strip()
    endpoint_url = resolve_endpoint_url(credentials)

    # GET /models is public on Straitly, so the key itself is checked on GET /key.
    response = _get(f"{endpoint_url}/key", api_key)
    if response.status_code in {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}:
        raise CredentialsValidateFailedError("Invalid Straitly API key")
    if response.status_code != HTTPStatus.OK:
        raise CredentialsValidateFailedError(
            f"Straitly credential validation failed with status {response.status_code}"
        )

    if model is None:
        return

    response = _get(f"{endpoint_url}/models", api_key)
    if response.status_code != HTTPStatus.OK:
        raise CredentialsValidateFailedError(
            f"Straitly model list request failed with status {response.status_code}"
        )
    try:
        payload = response.json()
    except ValueError as ex:
        raise CredentialsValidateFailedError("Straitly returned an invalid model list") from ex

    items = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        raise CredentialsValidateFailedError("Straitly returned an invalid model list")
    if model not in {item.get("id") for item in items if isinstance(item, dict)}:
        raise CredentialsValidateFailedError(
            f"Model '{model}' is not available to this Straitly API key"
        )
