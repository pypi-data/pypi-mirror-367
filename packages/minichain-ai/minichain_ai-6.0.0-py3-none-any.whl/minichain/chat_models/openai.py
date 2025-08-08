# src/minichain/chat_models/openai.py
"""
Provides a base class for chat models that use an OpenAI-compatible API.
This centralizes logic for both blocking (`invoke`) and streaming (`stream`)
API calls, reducing code duplication.
"""
import re
from typing import Union, List, Dict, Any, Iterator, cast
from openai import OpenAI, AzureOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionChunk

from .base import BaseChatModel
from ..core.types import BaseMessage, ChatResult, SystemMessage, HumanMessage, AIMessage, TokenUsage

class OpenAILikeChatModel(BaseChatModel):
    """
    A base class that handles core logic for OpenAI-compatible chat APIs.
    """
    # client: OpenAI | AzureOpenAI
    client: Union[OpenAI,AzureOpenAI]
    model_name: str
    temperature: float = 0.7
    max_tokens: Union[int, None] = None
    kwargs: Dict[str, Any]

    def _messages_to_openai_format(self, messages: List[BaseMessage]) -> List[ChatCompletionMessageParam]:
        """Converts Mini-Chain Message objects to the OpenAI API dictionary format."""
        openai_messages: List[Dict[str, str]] = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                openai_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, AIMessage):
                openai_messages.append({"role": "assistant", "content": msg.content})
            else: # HumanMessage or other
                openai_messages.append({"role": "user", "content": msg.content})
        return cast(List[ChatCompletionMessageParam], openai_messages)
    @staticmethod
    def _clean_response(text: str) -> str:
        """
        Removes preliminary "thinking" or "reasoning" blocks from the model's output.
        Handles both <think> tags and untagged reasoning paragraphs.
        """
        # First, remove any formal <think> blocks
        cleaned_text = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL).strip()
        
        # Second, heuristically check if the text *starts* with a reasoning block
        # that looks like the "Okay, the user is asking..." pattern.
        # This is more brittle but necessary for models that don't use tags.
        # We look for a paragraph that ends right before the "real" answer. A common
        # pattern is that the real answer starts with a direct address or statement.
        # This is complex to generalize, so we can start with a simpler rule:
        # If the text contains a well-known start to the answer, we can split on it.
        # For now, let's keep it simple and just rely on the <think> tag removal,
        # but this is where more advanced logic would go.
        # A more robust solution for untagged reasoning might require prompt engineering.
        
        return cleaned_text

    # --- NEW CORE METHOD: generate() ---
    # It now uses the streaming API for reliability and returns a rich object.
    def generate(self, input_data: Union[str, List[BaseMessage]]) -> ChatResult:
        """
        Generates a rich, structured response by consuming a stream for robustness.
        This is the primary method for getting a complete and cleaned response
        with full metadata.
        """
        messages: List[ChatCompletionMessageParam]
        if isinstance(input_data, str):
            messages = [{"role": "user", "content": input_data}]
        else:
            messages = self._messages_to_openai_format(input_data)
        
        completion_params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "stream": True,  # ALWAYS stream for the most reliable, complete response
            **self.kwargs,
        }
        
        if self.max_tokens is not None:
            completion_params["max_tokens"] = self.max_tokens

        stream = self.client.chat.completions.create(**completion_params)

        # Consume the stream to build the full response
        full_content = ""
        final_chunk: ChatCompletionChunk = None # type: ignore
        for chunk in stream:
            if chunk.choices:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    full_content += delta.content
            final_chunk = chunk

        # Clean the fully assembled response
        cleaned_content = self._clean_response(full_content)

        # Extract metadata from the final chunk if available
        # Note: Token usage is often in the final chunk's 'usage' field for some providers
        token_usage = TokenUsage()
        finish_reason = None
        model_name = self.model_name

        if final_chunk:
            model_name = final_chunk.model or self.model_name
            if final_chunk.choices:
                finish_reason = final_chunk.choices[0].finish_reason
            
            # OpenAI API compatible `usage` field in the last stream chunk
            if hasattr(final_chunk, 'usage') and final_chunk.usage:
                usage_data = final_chunk.usage
                token_usage = TokenUsage(
                    completion_tokens=usage_data.completion_tokens,
                    prompt_tokens=usage_data.prompt_tokens,
                    total_tokens=usage_data.total_tokens
                )
        
        return ChatResult(
            content=cleaned_content,
            model_name=model_name,
            token_usage=token_usage,
            finish_reason=finish_reason,
            raw=full_content, # Store the original, unclean content in `raw`
        )

    # --- NEW invoke() implementation ---
    # Now a simple, reliable wrapper around generate()
    def invoke(self, input_data: Union[str, List[BaseMessage]]) -> str:
        """
        Generates a clean, complete string response.
        This is a convenience wrapper around the `generate` method.
        """
        return self.generate(input_data).content

    # --- stream() is now for UI/raw streaming only ---
    def stream(self, input_data: Union[str, List[BaseMessage]]) -> Iterator[str]:
        """
        Generates a response as a raw, real-time stream of text chunks.
        This may include "thinking" blocks and is ideal for UI applications.
        """
        messages: List[ChatCompletionMessageParam]
        if isinstance(input_data, str):
            messages = [{"role": "user", "content": input_data}]
        else:
            messages = self._messages_to_openai_format(input_data)
        
        completion_params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "stream": True,
            **self.kwargs,
        }
        
        if self.max_tokens is not None:
            completion_params["max_tokens"] = self.max_tokens
            
        stream = self.client.chat.completions.create(**completion_params)
        
        for chunk in stream:
            if chunk.choices:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield content

    # def invoke(self, input_data: Union[str, List[BaseMessage]]) -> str:
    #     """Handles a standard, blocking request to the chat completions endpoint."""
    #     chunks = list(self.stream(input_data))
    #     # return "".join(chunks)
    #     full_response = "".join(chunks)
    # # Add post-processing to remove the think block
    #     clean_response = re.sub(r'<think>.*?</think>\s*', '', full_response, flags=re.DOTALL).strip()
    #     return clean_response
        
    # def generate(self, input_data: Union[str, List[BaseMessage]]) -> ChatResult:
    #     """Handles a non-streaming request to return a structured ChatResult."""
    #     messages: List[ChatCompletionMessageParam]
    #     if isinstance(input_data, str):
    #         messages = [{"role": "user", "content": input_data}]
    #     else:
    #         messages = self._messages_to_openai_format(input_data)
        
    #     completion_params = {
    #         "model": self.model_name,
    #         "messages": messages,
    #         "temperature": self.temperature,
    #         "stream": False,  # Ensure stream is False to get metadata
    #         **self.kwargs,
    #     }
        
    #     if self.max_tokens is not None:
    #         completion_params["max_tokens"] = self.max_tokens
            
    #     completion = self.client.chat.completions.create(**completion_params)

    #     usage_data = completion.usage
    #     token_usage = TokenUsage(
    #         completion_tokens=usage_data.completion_tokens if usage_data else None,
    #         prompt_tokens=usage_data.prompt_tokens if usage_data else None,
    #         total_tokens=usage_data.total_tokens if usage_data else None,
    #     )

    #     return ChatResult(
    #         content=completion.choices[0].message.content or "",
    #         model_name=completion.model,
    #         token_usage=token_usage,
    #         finish_reason=completion.choices[0].finish_reason,
    #         raw=completion,
    #     )

    # def stream(self, input_data: Union[str, List[BaseMessage]]) -> Iterator[str]:
    #     """Handles a streaming request to the chat completions endpoint."""
    #     messages: List[ChatCompletionMessageParam]
    #     if isinstance(input_data, str):
    #         messages = [{"role": "user", "content": input_data}]
    #     else:
    #         messages = self._messages_to_openai_format(input_data)
        
    #     completion_params = {
    #         "model": self.model_name,
    #         "messages": messages,
    #         "temperature": self.temperature,
    #         "stream": True,
    #         **self.kwargs,
    #     }
        
    #     if self.max_tokens is not None:
    #         completion_params["max_tokens"] = self.max_tokens
            
    #     stream = self.client.chat.completions.create(**completion_params)
        
    #     # ---  loop to handle all stream events ---
    #     for chunk in stream:
    #         # Check if the choices list is not empty. Some chunks are for
    #         # metadata and have an empty choices list.
    #         if chunk.choices:
    #             content = chunk.choices[0].delta.content
    #             # The content can also be None in some chunks, so check for that too.
    #             if content is not None:
    #                 yield content
  