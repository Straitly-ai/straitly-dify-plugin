import json
from unittest.mock import patch

import pytest
import requests
from dify_plugin.errors.model import CredentialsValidateFailedError

from models._credentials import resolve_endpoint_url, validate_model_access
from provider.straitly import StraitlyModelProvider


def _response(status: int, payload: object) -> requests.Response:
    result = requests.Response()
    result.status_code = status
    result._content = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    result.headers["Content-Type"] = "application/json"
    return result


def test_resolve_endpoint_url_defaults_and_trims() -> None:
    assert resolve_endpoint_url({}) == "https://api.straitly.ai/v1"
    assert resolve_endpoint_url({"endpoint_url": "  "}) == "https://api.straitly.ai/v1"
    assert (
        resolve_endpoint_url({"endpoint_url": "https://gateway.example.com/v1/"})
        == "https://gateway.example.com/v1"
    )


@patch("models._credentials.requests.get")
def test_provider_validation_uses_key_endpoint(get) -> None:
    get.return_value = _response(200, {"ok": True})
    provider = StraitlyModelProvider.__new__(StraitlyModelProvider)

    provider.validate_provider_credentials({"api_key": "sk-straitly-test"})

    get.assert_called_once_with(
        "https://api.straitly.ai/v1/key",
        headers={
            "Accept": "application/json",
            "Authorization": "Bearer sk-straitly-test",
        },
        timeout=(10, 30),
    )


@patch("models._credentials.requests.get")
def test_rejected_key_is_not_accepted_through_public_model_list(get) -> None:
    # GET /models answers 200 without a valid key, so it must never be the key check.
    get.side_effect = lambda url, **_: (
        _response(401, {"error": "invalid key"})
        if url.endswith("/key")
        else _response(200, {"object": "list", "data": [{"id": "z-ai/glm-5.3"}]})
    )

    with pytest.raises(CredentialsValidateFailedError, match="Invalid Straitly API key"):
        validate_model_access({"api_key": "sk-wrong"}, "z-ai/glm-5.3")


@patch("models._credentials.requests.get")
def test_model_validation_checks_model_availability(get) -> None:
    get.side_effect = lambda url, **_: (
        _response(200, {"ok": True})
        if url.endswith("/key")
        else _response(
            200, {"object": "list", "data": [{"id": "deepseek/deepseek-v4-1-flash-1017"}]}
        )
    )

    validate_model_access({"api_key": "sk-straitly-test"}, "deepseek/deepseek-v4-1-flash-1017")

    with pytest.raises(CredentialsValidateFailedError, match="not available"):
        validate_model_access({"api_key": "sk-straitly-test"}, "unknown/model")


def test_missing_api_key_rejected() -> None:
    with pytest.raises(CredentialsValidateFailedError, match="API key is required"):
        validate_model_access({"api_key": "  "})


@pytest.mark.parametrize("status", [401, 403])
@patch("models._credentials.requests.get")
def test_invalid_key_statuses_do_not_leak_body(get, status: int) -> None:
    get.return_value = _response(status, {"error": {"message": "sensitive detail"}})

    with pytest.raises(CredentialsValidateFailedError, match="Invalid Straitly API key") as err:
        validate_model_access({"api_key": "secret"})

    assert "sensitive detail" not in str(err.value)


@patch("models._credentials.requests.get")
def test_upstream_failure_hides_response_body(get) -> None:
    get.return_value = _response(503, {"error": {"message": "internal detail"}})

    with pytest.raises(
        CredentialsValidateFailedError,
        match="validation failed with status 503",
    ) as err:
        validate_model_access({"api_key": "secret"})

    assert "internal detail" not in str(err.value)


@patch("models._credentials.requests.get")
def test_invalid_json_is_rejected(get) -> None:
    get.side_effect = lambda url, **_: (
        _response(200, {"ok": True}) if url.endswith("/key") else _response(200, b"not-json")
    )

    with pytest.raises(CredentialsValidateFailedError, match="invalid model list"):
        validate_model_access({"api_key": "secret"}, "z-ai/glm-5.3")


def test_bundled_models_are_listed_and_consistent() -> None:
    from pathlib import Path

    import yaml

    llm_dir = Path(__file__).resolve().parent.parent / "models" / "llm"
    position = yaml.safe_load((llm_dir / "_position.yaml").read_text())
    defined = {
        yaml.safe_load(path.read_text())["model"]
        for path in llm_dir.glob("*.yaml")
        if path.name != "_position.yaml"
    }
    assert sorted(position) == sorted(defined)
    assert len(position) == len(set(position))
