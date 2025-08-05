import json
from time import time
from typing import Any

from openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk,
    Choice,
    ChoiceDelta,
)

try:
    from google.genai import types
except ImportError:
    msg = "google-genai is not installed. Please install it with `pip install any-llm-sdk[google]`"
    raise ImportError(msg)


def _convert_tool_spec(openai_tools: list[dict[str, Any]]) -> list[types.Tool]:
    """Convert OpenAI tool specification to Google GenAI format."""
    function_declarations = []

    for tool in openai_tools:
        if tool.get("type") != "function":
            continue

        function = tool["function"]
        parameters_dict = {
            "type": "object",
            "properties": {
                param_name: {
                    "type": param_info.get("type", "string"),
                    "description": param_info.get("description", ""),
                    **({"enum": param_info["enum"]} if "enum" in param_info else {}),
                }
                for param_name, param_info in function["parameters"]["properties"].items()
            },
            "required": function["parameters"].get("required", []),
        }

        function_declarations.append(
            types.FunctionDeclaration(
                name=function["name"],
                description=function.get("description", ""),
                parameters=types.Schema(**parameters_dict),
            )
        )

    return [types.Tool(function_declarations=function_declarations)]


def _convert_messages(messages: list[dict[str, Any]]) -> list[types.Content]:
    """Convert messages to Google GenAI format."""
    formatted_messages = []

    for message in messages:
        if message["role"] == "system":
            # System messages are treated as user messages in GenAI
            parts = [types.Part.from_text(text=message["content"])]
            formatted_messages.append(types.Content(role="user", parts=parts))
        elif message["role"] == "user":
            parts = [types.Part.from_text(text=message["content"])]
            formatted_messages.append(types.Content(role="user", parts=parts))
        elif message["role"] == "assistant":
            if "tool_calls" in message and message["tool_calls"]:
                # Handle function calls
                tool_call = message["tool_calls"][0]  # Assuming single function call for now
                function_call = tool_call["function"]

                parts = [
                    types.Part.from_function_call(
                        name=function_call["name"], args=json.loads(function_call["arguments"])
                    )
                ]
            else:
                # Handle regular text messages
                parts = [types.Part.from_text(text=message["content"])]

            formatted_messages.append(types.Content(role="model", parts=parts))
        elif message["role"] == "tool":
            # Convert tool result to function response
            try:
                content_json = json.loads(message["content"])
                part = types.Part.from_function_response(name=message.get("name", "unknown"), response=content_json)
                formatted_messages.append(types.Content(role="function", parts=[part]))
            except json.JSONDecodeError:
                # If not JSON, treat as text
                part = types.Part.from_function_response(
                    name=message.get("name", "unknown"), response={"result": message["content"]}
                )
                formatted_messages.append(types.Content(role="function", parts=[part]))

    return formatted_messages


def _create_openai_chunk_from_google_chunk(
    response: types.GenerateContentResponse,
) -> ChatCompletionChunk:
    """Convert a Google GenerateContentResponse to an OpenAI ChatCompletionChunk."""

    assert response.candidates
    candidate = response.candidates[0]
    assert candidate.content
    assert candidate.content.parts
    part = candidate.content.parts[0]

    delta = ChoiceDelta(content=part.text, role="assistant")

    choice = Choice(
        index=0,
        delta=delta,
        finish_reason="stop" if getattr(candidate.finish_reason, "value", None) == "STOP" else None,
    )

    return ChatCompletionChunk(
        id=f"chatcmpl-{time()}",  # Google doesn't provide an ID in the chunk
        choices=[choice],
        created=int(time()),
        model=str(response.model_version),
        object="chat.completion.chunk",
    )
