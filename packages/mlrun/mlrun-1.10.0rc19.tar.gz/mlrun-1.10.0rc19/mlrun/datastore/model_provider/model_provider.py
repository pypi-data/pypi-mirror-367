# Copyright 2025 Iguazio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from collections.abc import Awaitable
from typing import Any, Callable, Optional, Union

import mlrun.errors
from mlrun.datastore.remote_client import (
    BaseRemoteClient,
)


class ModelProvider(BaseRemoteClient):
    """
    The ModelProvider class is an abstract base for integrating with external
    model providers, primarily generative AI (GenAI) services.

    Designed to be subclassed, it defines a consistent interface and shared
    functionality for tasks such as text generation, embeddings, and invoking
    fine-tuned models. Subclasses should implement provider-specific logic,
    including SDK client initialization, model invocation, and custom operations.

    Key Features:
    - Establishes a consistent, reusable client management for model provider integrations.
    - Simplifies GenAI service integration by abstracting common operations.
    - Reduces duplication through shared components for common tasks.
    - Holds default invocation parameters (e.g., temperature, max_tokens) to avoid boilerplate
    code and promote consistency.
    """

    support_async = False

    def __init__(
        self,
        parent,
        kind,
        name,
        endpoint="",
        secrets: Optional[dict] = None,
        default_invoke_kwargs: Optional[dict] = None,
    ):
        super().__init__(
            parent=parent, name=name, kind=kind, endpoint=endpoint, secrets=secrets
        )
        self.default_invoke_kwargs = default_invoke_kwargs or {}
        self._client = None
        self._async_client = None

    def get_client_options(self) -> dict:
        """
        Returns a dictionary containing credentials and configuration
        options required for client creation.

        :return:           A dictionary with client-specific settings.
        """
        return {}

    def load_client(self) -> None:
        """
        Initializes the SDK client for the model provider with the given keyword arguments
        and assigns it to an instance attribute (e.g., self._client).

        Subclasses should override this method to:
        - Create and configure the provider-specific client instance.
        - Assign the client instance to self._client.
        """

        raise NotImplementedError("load_client method is not implemented")

    @property
    def client(self) -> Any:
        return self._client

    @property
    def model(self) -> Optional[str]:
        """
        Returns the model identifier used by the underlying SDK.

        :return: A string representing the model ID, or None if not set.
        """
        return self.endpoint

    def get_invoke_kwargs(self, invoke_kwargs) -> dict:
        kwargs = self.default_invoke_kwargs.copy()
        kwargs.update(invoke_kwargs)
        return kwargs

    @property
    def async_client(self) -> Any:
        if not self.support_async:
            raise mlrun.errors.MLRunInvalidArgumentError(
                f"{self.__class__.__name__} does not support async operations"
            )
        return self._async_client

    def custom_invoke(self, operation: Optional[Callable], **invoke_kwargs) -> Any:
        """
        Invokes a model operation from a provider (e.g., OpenAI, Hugging Face, etc.) with the given keyword arguments.

        Useful for dynamically calling model methods like text generation, chat completions, or image generation.
        The operation must be a callable that accepts keyword arguments.

        :param operation:       A callable representing the model operation (e.g., a client method).
        :param invoke_kwargs:   Keyword arguments to pass to the operation.
        :return:                The full response returned by the operation.
        """
        raise NotImplementedError("custom_invoke method is not implemented")

    async def async_custom_invoke(
        self, operation: Optional[Callable[..., Awaitable[Any]]], **invoke_kwargs
    ) -> Any:
        """
        Asynchronously invokes a model operation from a provider (e.g., OpenAI, Hugging Face, etc.)
        with the given keyword arguments.

        The operation must be an async callable (e.g., a method from an async client) that accepts keyword arguments.

        :param operation:       An async callable representing the model operation (e.g., an async_client method).
        :param invoke_kwargs:   Keyword arguments to pass to the operation.
        :return:                The full response returned by the awaited operation.
        """
        raise NotImplementedError("async_custom_invoke is not implemented")

    def invoke(
        self,
        messages: Optional[list[dict]] = None,
        as_str: bool = False,
        **invoke_kwargs,
    ) -> Union[str, Any]:
        """
        Invokes a generative AI model with the provided messages and additional parameters.
        This method is designed to be a flexible interface for interacting with various
        generative AI backends (e.g., OpenAI, Hugging Face, etc.). It allows users to send
        a list of messages (following a standardized format) and receive a response. The
        response can be returned as plain text or in its full structured format, depending
        on the `as_str` parameter.

        :param messages:    A list of dictionaries representing the conversation history or input messages.
                            Each dictionary should follow the format::
                            {"role": "system"| "user" | "assistant" ..., "content": "Message content as a string"}
                            Example:

                            .. code-block:: json

                                [
                                    {"role": "system", "content": "You are a helpful assistant."},
                                    {"role": "user", "content": "What is the capital of France?"}
                                ]

                            This format is consistent across all backends. Defaults to None if no messages
                            are provided.

        :param as_str:      A boolean flag indicating whether to return the response as a plain string.
                            - If True, the function extracts and returns the main content of the first
                            response.
                            - If False, the function returns the full response object,
                            which may include additional metadata or multiple response options.
                            Defaults to False.

        :param invoke_kwargs:
                            Additional keyword arguments to be passed to the underlying model API call.
                            These can include parameters such as temperature, max tokens, etc.,
                            depending on the capabilities of the specific backend being used.

        :return:
                            - If `as_str` is True: Returns the main content of the first response as a string.
                            - If `as_str` is False: Returns the full response object.

        """
        raise NotImplementedError("invoke method is not implemented")

    async def async_invoke(
        self,
        messages: Optional[list[dict]] = None,
        as_str: bool = False,
        **invoke_kwargs,
    ) -> Union[str, Any]:
        """Async version of `invoke`. See `invoke` for full documentation."""
        raise NotImplementedError("async_invoke is not implemented")
