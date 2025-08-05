import os
from typing import Any

try:
    import instructor
except ImportError:
    msg = "instructor is not installed. Please install it with `pip install any-llm-sdk[sambanova]`"
    raise ImportError(msg)

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from openai._streaming import Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

from any_llm.provider import convert_instructor_response
from any_llm.providers.openai.base import BaseOpenAIProvider


class SambanovaProvider(BaseOpenAIProvider):
    API_BASE = "https://api.sambanova.ai/v1/"
    ENV_API_KEY_NAME = "SAMBANOVA_API_KEY"
    PROVIDER_NAME = "SambaNova"
    PROVIDER_DOCUMENTATION_URL = "https://sambanova.ai/"

    def completion(
        self, model: str, messages: list[dict[str, Any]], **kwargs: Any
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        """Make the API call to SambaNova service with instructor for structured output."""
        client = OpenAI(
            base_url=self.config.api_base or self.API_BASE or os.getenv("OPENAI_API_BASE"),
            api_key=self.config.api_key,
        )

        if "response_format" in kwargs:
            instructor_client = instructor.from_openai(client)
            response_format = kwargs.pop("response_format")
            response = instructor_client.chat.completions.create(
                model=model,
                messages=messages,  # type: ignore[arg-type]
                response_model=response_format,
                **kwargs,
            )
            return convert_instructor_response(response, model, self.PROVIDER_NAME)
        else:
            return client.chat.completions.create(
                model=model,
                messages=messages,  # type: ignore[arg-type]
                **kwargs,
            )
