# pickle_openai/__init__.py
import base64
import json
import os
import pathlib
import pickle
import typing

import httpx
import openai
import pydantic
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

__version__ = pathlib.Path(__file__).parent.joinpath("VERSION").read_text().strip()


def is_azure_openai(
    client: (
        openai.OpenAI
        | openai.AsyncOpenAI
        | openai.AzureOpenAI
        | openai.AsyncAzureOpenAI
    ),
) -> bool:
    """Check if client is Azure OpenAI instance."""
    for k in client.__dict__.keys():
        if "azure" in k:
            return True
    return False


DEFAULT_MAX_RETRIES = 2
PRIMITIVE_TYPE: typing.TypeAlias = str | int | float | bool | None


class PickledOpenAI(pydantic.BaseModel):
    api_key: pydantic.SecretStr | None = None
    api_version: str | None = None
    azure_ad_token: pydantic.SecretStr | None = None
    azure_deployment: str | None = None
    azure_endpoint: str | None = None
    base_url: str | None = None
    default_headers: typing.Dict[str, str] | None = None
    default_query: typing.Dict[str, PRIMITIVE_TYPE] | None = None
    max_retries: int = DEFAULT_MAX_RETRIES
    openai_version: str = openai.__version__
    organization: str | None = None
    pickle_openai_version: str = __version__
    project: str | None = None
    timeout: float | dict[str, float | None] | None = None
    webhook_secret: pydantic.SecretStr | None = None
    websocket_base_url: str | None = None
    websocket_base_url: str | None = None

    @classmethod
    def from_openai(
        cls,
        client: (
            openai.OpenAI
            | openai.AsyncOpenAI
            | openai.AzureOpenAI
            | openai.AsyncAzureOpenAI
        ),
    ) -> "PickledOpenAI":
        """Create PickledOpenAI from OpenAI client instance."""
        if is_azure_openai(client):
            client = typing.cast(openai.AzureOpenAI | openai.AsyncAzureOpenAI, client)
            return cls.from_azure_openai(client)
        else:
            return cls(
                api_key=pydantic.SecretStr(client.api_key),
                organization=client.organization,
                project=client.project,
                webhook_secret=(
                    pydantic.SecretStr(client.webhook_secret)
                    if client.webhook_secret
                    else None
                ),
                websocket_base_url=(
                    str(client.websocket_base_url)
                    if client.websocket_base_url
                    else client.websocket_base_url
                ),
                openai_version=client._version,
                base_url=str(client._base_url),
                max_retries=client.max_retries,
                timeout=(
                    client.timeout.as_dict()
                    if isinstance(client.timeout, httpx.Timeout)
                    else client.timeout if client.timeout else None
                ),
                default_headers=dict(client._custom_headers),
                default_query=dict(client._custom_query),  # type: ignore
            )

    @classmethod
    def from_azure_openai(
        cls, client: openai.AzureOpenAI | openai.AsyncAzureOpenAI
    ) -> "PickledOpenAI":
        """Create PickledOpenAI from Azure OpenAI client instance."""
        return cls(
            api_key=pydantic.SecretStr(client.api_key) if client.api_key else None,
            api_version=client._api_version,
            organization=client.organization,
            project=client.project,
            webhook_secret=(
                pydantic.SecretStr(client.webhook_secret)
                if client.webhook_secret
                else None
            ),
            websocket_base_url=(
                str(client.websocket_base_url)
                if client.websocket_base_url
                else client.websocket_base_url
            ),
            openai_version=client._version,
            base_url=str(client._base_url),
            max_retries=client.max_retries,
            timeout=(
                client.timeout.as_dict()
                if isinstance(client.timeout, httpx.Timeout)
                else client.timeout if client.timeout else None
            ),
            default_headers=dict(client._custom_headers),
            default_query=dict(client._custom_query),  # type: ignore
            azure_ad_token=(
                pydantic.SecretStr(client._azure_ad_token)
                if client._azure_ad_token
                else None
            ),
            azure_deployment=client._azure_deployment,
            azure_endpoint=(
                str(client._azure_endpoint) if client._azure_endpoint else None
            ),
        )

    @classmethod
    def pickle_loads(cls, encrypted_pickle: str, password: str) -> "PickledOpenAI":
        """Deserialize encrypted pickle string back to PickledOpenAI instance."""
        try:
            raw = base64.urlsafe_b64decode(encrypted_pickle.encode("ascii"))
            salt, token = raw[:16], raw[16:]  # 16-byte salt prefix
            key = _derive_key(password, salt)
            data = Fernet(key).decrypt(token)  # may raise InvalidToken
            json_obj = pickle.loads(data)
            return cls.model_validate_json(json_obj)
        except (InvalidToken, ValueError, pickle.UnpicklingError) as exc:
            raise ValueError("Invalid password or corrupted data") from exc

    def pickle_dumps(self, password: str) -> str:
        """Serialize this instance to encrypted string for secure storage."""
        # 1. Pickle this object as a dict (safer than pickling the raw instance)
        pickled: bytes = pickle.dumps(self.to_unsafe_json_serializable())

        # 2. Derive a key from `password` and a fresh random salt
        salt = os.urandom(16)  # 128-bit salt
        key = _derive_key(password, salt)

        # 3. Encrypt with Fernet
        token = Fernet(key).encrypt(pickled)

        # 4. Pack salt+token and return url-safe base64 text
        return base64.urlsafe_b64encode(salt + token).decode("ascii")

    def to_openai(self) -> openai.AsyncOpenAI | openai.AsyncAzureOpenAI:
        """Convert to AsyncOpenAI or AsyncAzureOpenAI client."""
        if any([self.azure_ad_token, self.azure_deployment, self.azure_endpoint]):
            if self.azure_endpoint is None:
                raise ValueError("The azure_endpoint is required for Azure OpenAI")
            return openai.AsyncAzureOpenAI(
                azure_endpoint=self.azure_endpoint,
                azure_deployment=self.azure_deployment,
                api_version=self.api_version,
                api_key=self.api_key.get_secret_value() if self.api_key else None,
                azure_ad_token=(
                    self.azure_ad_token.get_secret_value()
                    if self.azure_ad_token
                    else None
                ),
                organization=self.organization,
                project=self.project,
                webhook_secret=(
                    self.webhook_secret.get_secret_value()
                    if self.webhook_secret
                    else None
                ),
                websocket_base_url=self.websocket_base_url,
                timeout=(
                    httpx.Timeout(**self.timeout)
                    if isinstance(self.timeout, dict)
                    else self.timeout
                ),
                max_retries=self.max_retries,
                default_headers=self.default_headers,
                default_query=self.default_query,
            )
        else:
            return openai.AsyncOpenAI(
                api_key=self.api_key.get_secret_value() if self.api_key else None,
                organization=self.organization,
                project=self.project,
                webhook_secret=(
                    self.webhook_secret.get_secret_value()
                    if self.webhook_secret
                    else None
                ),
                base_url=self.base_url,
                websocket_base_url=self.websocket_base_url,
                timeout=(
                    httpx.Timeout(**self.timeout)
                    if isinstance(self.timeout, dict)
                    else self.timeout
                ),
                max_retries=self.max_retries,
                default_headers=self.default_headers,
                default_query=self.default_query,
            )

    def to_openai_sync(self) -> openai.OpenAI | openai.AzureOpenAI:
        """Convert to sync OpenAI or AzureOpenAI client."""
        if any([self.azure_ad_token, self.azure_deployment, self.azure_endpoint]):
            if self.azure_endpoint is None:
                raise ValueError("The azure_endpoint is required for Azure OpenAI")
            return openai.AzureOpenAI(
                azure_endpoint=self.azure_endpoint,
                azure_deployment=self.azure_deployment,
                api_version=self.api_version,
                api_key=self.api_key.get_secret_value() if self.api_key else None,
                azure_ad_token=(
                    self.azure_ad_token.get_secret_value()
                    if self.azure_ad_token
                    else None
                ),
                organization=self.organization,
                webhook_secret=(
                    self.webhook_secret.get_secret_value()
                    if self.webhook_secret
                    else None
                ),
                websocket_base_url=self.websocket_base_url,
                timeout=(
                    httpx.Timeout(**self.timeout)
                    if isinstance(self.timeout, dict)
                    else self.timeout
                ),
                max_retries=self.max_retries,
                default_headers=self.default_headers,
                default_query=self.default_query,
            )
        else:
            return openai.OpenAI(
                api_key=self.api_key.get_secret_value() if self.api_key else None,
                organization=self.organization,
                project=self.project,
                webhook_secret=(
                    self.webhook_secret.get_secret_value()
                    if self.webhook_secret
                    else None
                ),
                base_url=self.base_url,
                websocket_base_url=self.websocket_base_url,
                timeout=(
                    httpx.Timeout(**self.timeout)
                    if isinstance(self.timeout, dict)
                    else self.timeout
                ),
                max_retries=self.max_retries,
                default_headers=self.default_headers,
                default_query=self.default_query,
            )

    def to_unsafe_json_serializable(self) -> str:
        """Export to JSON string with secrets exposed."""
        data = json.loads(self.model_dump_json())
        data["api_key"] = self.api_key.get_secret_value() if self.api_key else None
        data["azure_ad_token"] = (
            self.azure_ad_token.get_secret_value() if self.azure_ad_token else None
        )
        data["webhook_secret"] = (
            self.webhook_secret.get_secret_value() if self.webhook_secret else None
        )
        return json.dumps(data)


def _derive_key(password: str, salt: bytes, iterations: int = 390_000) -> bytes:
    """Derive Fernet key from password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
