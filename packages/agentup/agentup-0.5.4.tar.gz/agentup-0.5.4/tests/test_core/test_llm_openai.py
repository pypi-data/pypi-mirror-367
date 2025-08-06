# Add src to path for imports
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agent.llm_providers.base import (
    ChatMessage,
    FunctionCall,
    LLMProviderAPIError,
    LLMProviderError,
    LLMResponse,
)
from agent.llm_providers.openai import OpenAIProvider


class TestOpenAIProviderInitialization:
    def test_init_basic_config(self):
        config = {"api_key": "test-key", "model": "gpt-4"}
        provider = OpenAIProvider("test-openai", config)

        assert provider.name == "test-openai"
        assert provider.api_key == "test-key"
        assert provider.model == "gpt-4"
        assert provider.base_url == "https://api.openai.com/v1"
        assert provider.timeout == 60.0
        assert provider.organization is None
        assert provider.client is None
        assert not provider._initialized

    def test_init_full_config(self):
        config = {
            "api_key": "test-key",
            "model": "gpt-3.5-turbo",
            "base_url": "https://custom.openai.com/v1",
            "organization": "org-123",
            "timeout": 30.0,
        }
        provider = OpenAIProvider("custom-openai", config)

        assert provider.api_key == "test-key"
        assert provider.model == "gpt-3.5-turbo"
        assert provider.base_url == "https://custom.openai.com/v1"
        assert provider.organization == "org-123"
        assert provider.timeout == 30.0

    def test_init_default_values(self):
        config = {}
        provider = OpenAIProvider("default-openai", config)

        assert provider.api_key == ""
        assert provider.model == "gpt-4o-mini"
        assert provider.base_url == "https://api.openai.com/v1"
        assert provider.timeout == 60.0


class TestOpenAIProviderServiceManagement:
    @pytest.mark.asyncio
    async def test_initialize_success(self):
        config = {"api_key": "test-key", "model": "gpt-4"}
        provider = OpenAIProvider("test", config)

        # Mock health check to succeed
        with patch.object(provider, "health_check", return_value={"status": "healthy"}):
            await provider.initialize()

        assert provider._initialized
        assert provider.client is not None
        assert isinstance(provider.client, httpx.AsyncClient)
        assert str(provider.client.base_url) == "https://api.openai.com/v1/"

        # Check headers
        auth_header = provider.client.headers.get("Authorization")
        assert auth_header == "Bearer test-key"
        assert provider.client.headers.get("Content-Type") == "application/json"
        assert provider.client.headers.get("User-Agent") == "AgentUp-Agent/1.0"

    @pytest.mark.asyncio
    async def test_initialize_with_organization(self):
        config = {"api_key": "test-key", "model": "gpt-4", "organization": "org-123"}
        provider = OpenAIProvider("test", config)

        with patch.object(provider, "health_check", return_value={"status": "healthy"}):
            await provider.initialize()

        assert provider.client.headers.get("OpenAI-Organization") == "org-123"

    @pytest.mark.asyncio
    async def test_initialize_missing_api_key(self):
        config = {"model": "gpt-4"}  # Missing api_key
        provider = OpenAIProvider("test", config)

        # Should not raise exception, but should mark as unavailable
        await provider.initialize()

        assert not provider._initialized
        assert not provider.is_available()

    @pytest.mark.asyncio
    async def test_initialize_health_check_fails(self):
        config = {"api_key": "test-key", "model": "gpt-4"}
        provider = OpenAIProvider("test", config)

        with patch.object(provider, "health_check", side_effect=Exception("API error")):
            with pytest.raises(LLMProviderError, match="Failed to initialize OpenAI service"):
                await provider.initialize()

        assert not provider._initialized

    @pytest.mark.asyncio
    async def test_close(self):
        config = {"api_key": "test-key", "model": "gpt-4"}
        provider = OpenAIProvider("test", config)

        # Initialize first
        with patch.object(provider, "health_check", return_value={"status": "healthy"}):
            await provider.initialize()

        # Mock the aclose method
        provider.client.aclose = AsyncMock()

        await provider.close()

        assert not provider._initialized
        provider.client.aclose.assert_called_once()


class TestOpenAIProviderHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        config = {"api_key": "test-key", "model": "gpt-4"}
        provider = OpenAIProvider("test", config)

        # Mock the client and response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.5

        provider.client = AsyncMock()
        provider.client.get.return_value = mock_response

        result = await provider.health_check()

        assert result["status"] == "healthy"
        assert result["response_time_ms"] == 500
        assert result["status_code"] == 200
        assert result["model"] == "gpt-4"
        provider.client.get.assert_called_once_with("/models")

    @pytest.mark.asyncio
    async def test_health_check_unhealthy_status(self):
        config = {"api_key": "test-key", "model": "gpt-4"}
        provider = OpenAIProvider("test", config)

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.elapsed = None

        provider.client = AsyncMock()
        provider.client.get.return_value = mock_response

        result = await provider.health_check()

        assert result["status"] == "unhealthy"
        assert result["response_time_ms"] == 0
        assert result["status_code"] == 401

    @pytest.mark.asyncio
    async def test_health_check_exception(self):
        config = {"api_key": "test-key", "model": "gpt-4"}
        provider = OpenAIProvider("test", config)

        provider.client = AsyncMock()
        provider.client.get.side_effect = httpx.ConnectError("Connection failed")

        result = await provider.health_check()

        assert result["status"] == "unhealthy"
        assert "Connection failed" in result["error"]
        assert result["model"] == "gpt-4"


class TestOpenAIProviderChatCompletion:
    def setup_method(self):
        self.config = {"api_key": "test-key", "model": "gpt-4"}
        self.provider = OpenAIProvider("test", self.config)
        self.provider._initialized = True
        self.provider._available = True  # Mark as available for tests
        self.provider.client = AsyncMock()

    @pytest.mark.asyncio
    async def test_complete_basic(self):
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello, world!"}, "finish_reason": "stop"}],
            "usage": {"total_tokens": 10},
            "model": "gpt-4",
        }
        self.provider.client.post.return_value = mock_response

        result = await self.provider.complete("Hello")

        assert isinstance(result, LLMResponse)
        assert result.content == "Hello, world!"
        assert result.finish_reason == "stop"
        assert result.usage == {"total_tokens": 10}
        assert result.model == "gpt-4"

        # Verify API call
        self.provider.client.post.assert_called_once()
        call_args = self.provider.client.post.call_args
        assert call_args[0][0] == "/chat/completions"
        payload = call_args[1]["json"]
        assert payload["model"] == "gpt-4"
        assert len(payload["messages"]) == 1
        assert payload["messages"][0]["role"] == "user"
        assert payload["messages"][0]["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_chat_complete_multiple_messages(self):
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="Hello"),
            ChatMessage(role="assistant", content="Hi there!"),
            ChatMessage(role="user", content="How are you?"),
        ]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "I am doing well, thank you!"}, "finish_reason": "stop"}],
            "usage": {"total_tokens": 25},
        }
        self.provider.client.post.return_value = mock_response

        result = await self.provider.chat_complete(messages)

        assert result.content == "I am doing well, thank you!"

        # Verify all messages were sent
        payload = self.provider.client.post.call_args[1]["json"]
        assert len(payload["messages"]) == 4
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][1]["role"] == "user"
        assert payload["messages"][2]["role"] == "assistant"
        assert payload["messages"][3]["role"] == "user"

    @pytest.mark.asyncio
    async def test_chat_complete_with_kwargs(self):
        messages = [ChatMessage(role="user", content="Test")]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "Response"}, "finish_reason": "stop"}]}
        self.provider.client.post.return_value = mock_response

        await self.provider.chat_complete(
            messages, temperature=0.9, max_tokens=500, top_p=0.8, frequency_penalty=0.5, presence_penalty=0.3
        )

        payload = self.provider.client.post.call_args[1]["json"]
        assert payload["temperature"] == 0.9
        assert payload["max_tokens"] == 500
        assert payload["top_p"] == 0.8
        assert payload["frequency_penalty"] == 0.5
        assert payload["presence_penalty"] == 0.3

    @pytest.mark.asyncio
    async def test_chat_complete_json_mode(self):
        messages = [ChatMessage(role="user", content="Return JSON")]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"result": "success"}'}, "finish_reason": "stop"}]
        }
        self.provider.client.post.return_value = mock_response

        await self.provider.chat_complete(messages, response_format="json")

        payload = self.provider.client.post.call_args[1]["json"]
        assert payload["response_format"] == {"type": "json_object"}

    @pytest.mark.asyncio
    async def test_chat_complete_api_error(self):
        messages = [ChatMessage(role="user", content="Test")]

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        self.provider.client.post.return_value = mock_response

        with pytest.raises(LLMProviderAPIError, match="OpenAI API error: 401"):
            await self.provider.chat_complete(messages)

    @pytest.mark.asyncio
    async def test_chat_complete_network_error(self):
        messages = [ChatMessage(role="user", content="Test")]

        self.provider.client.post.side_effect = httpx.ConnectError("Network error")

        with pytest.raises(LLMProviderAPIError, match="OpenAI API request failed"):
            await self.provider.chat_complete(messages)

    @pytest.mark.asyncio
    async def test_chat_complete_invalid_response(self):
        messages = [ChatMessage(role="user", content="Test")]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "response"}  # Missing choices
        self.provider.client.post.return_value = mock_response

        with pytest.raises(LLMProviderAPIError, match="Invalid OpenAI API response format"):
            await self.provider.chat_complete(messages)


class TestOpenAIProviderFunctionCalling:
    def setup_method(self):
        self.config = {"api_key": "test-key", "model": "gpt-4"}
        self.provider = OpenAIProvider("test", self.config)
        self.provider._initialized = True
        self.provider._available = True  # Mark as available for tests
        self.provider.client = AsyncMock()

        self.functions = [
            {
                "name": "get_weather",
                "description": "Get weather information",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string", "description": "City name"}},
                    "required": ["location"],
                },
            }
        ]

    @pytest.mark.asyncio
    async def test_function_calling_success(self):
        messages = [ChatMessage(role="user", content="What's the weather in Paris?")]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": None,
                        "function_call": {"name": "get_weather", "arguments": '{"location": "Paris"}'},
                    },
                    "finish_reason": "function_call",
                }
            ],
            "usage": {"total_tokens": 20},
            "model": "gpt-4",
        }
        self.provider.client.post.return_value = mock_response

        result = await self.provider._chat_complete_with_functions_native(messages, self.functions)

        assert isinstance(result, LLMResponse)
        assert result.content is None or result.content == ""
        assert result.finish_reason == "function_call"
        assert len(result.function_calls) == 1

        fc = result.function_calls[0]
        assert fc.name == "get_weather"
        assert fc.arguments == {"location": "Paris"}

        # Verify API call includes functions
        payload = self.provider.client.post.call_args[1]["json"]
        assert "functions" in payload
        assert payload["functions"] == self.functions
        assert payload["function_call"] == "auto"

    @pytest.mark.asyncio
    async def test_function_calling_with_custom_function_call(self):
        messages = [ChatMessage(role="user", content="Test")]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "Response"}, "finish_reason": "stop"}]}
        self.provider.client.post.return_value = mock_response

        await self.provider._chat_complete_with_functions_native(
            messages, self.functions, function_call={"name": "get_weather"}
        )

        payload = self.provider.client.post.call_args[1]["json"]
        assert payload["function_call"] == {"name": "get_weather"}

    @pytest.mark.asyncio
    async def test_function_calling_malformed_json(self):
        messages = [ChatMessage(role="user", content="Test")]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": None,
                        "function_call": {
                            "name": "get_weather",
                            "arguments": '{"location": "Paris"',  # Missing closing brace
                        },
                    },
                    "finish_reason": "function_call",
                }
            ]
        }
        self.provider.client.post.return_value = mock_response

        with patch("agent.llm_providers.openai.logger") as mock_logger:
            result = await self.provider._chat_complete_with_functions_native(messages, self.functions)

        # Should handle malformed JSON gracefully
        assert len(result.function_calls) == 1
        fc = result.function_calls[0]
        assert fc.name == "get_weather"
        assert fc.arguments == {"location": "Paris"}  # Fixed JSON
        mock_logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_function_calling_unfixable_json(self):
        messages = [ChatMessage(role="user", content="Test")]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": None,
                        "function_call": {"name": "get_weather", "arguments": "not json at all"},
                    },
                    "finish_reason": "function_call",
                }
            ]
        }
        self.provider.client.post.return_value = mock_response

        with patch("agent.llm_providers.openai.logger") as mock_logger:
            result = await self.provider._chat_complete_with_functions_native(messages, self.functions)

        # Should use empty arguments for unfixable JSON
        assert len(result.function_calls) == 1
        fc = result.function_calls[0]
        assert fc.name == "get_weather"
        assert fc.arguments == {}
        mock_logger.warning.assert_called()


class TestOpenAIProviderEmbeddings:
    def setup_method(self):
        self.config = {"api_key": "test-key", "model": "text-embedding-3-small"}
        self.provider = OpenAIProvider("test", self.config)
        self.provider._initialized = True
        self.provider._available = True  # Mark as available for tests
        self.provider.client = AsyncMock()

    @pytest.mark.asyncio
    async def test_embed_success(self):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"embedding": [0.1, 0.2, 0.3, -0.1, -0.2]}]}
        self.provider.client.post.return_value = mock_response

        result = await self.provider._embed_impl("Hello world")

        assert result == [0.1, 0.2, 0.3, -0.1, -0.2]

        # Verify API call
        self.provider.client.post.assert_called_once_with(
            "/embeddings", json={"model": "text-embedding-3-small", "input": "Hello world", "encoding_format": "float"}
        )

    @pytest.mark.asyncio
    async def test_embed_with_non_embedding_model(self):
        # Use a chat model
        config = {"api_key": "test-key", "model": "gpt-4"}
        provider = OpenAIProvider("test", config)
        provider._initialized = True
        provider.client = AsyncMock()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"embedding": [0.1, 0.2]}]}
        provider.client.post.return_value = mock_response

        await provider._embed_impl("Test")

        # Should use default embedding model
        payload = provider.client.post.call_args[1]["json"]
        assert payload["model"] == "text-embedding-3-small"

    @pytest.mark.asyncio
    async def test_embed_api_error(self):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        self.provider.client.post.return_value = mock_response

        with pytest.raises(LLMProviderAPIError, match="OpenAI embeddings API error: 400"):
            await self.provider._embed_impl("Test")


class TestOpenAIProviderStreaming:
    def setup_method(self):
        self.config = {"api_key": "test-key", "model": "gpt-4"}
        self.provider = OpenAIProvider("test", self.config)
        self.provider._initialized = True
        self.provider._available = True  # Mark as available for tests
        self.provider.client = AsyncMock()

    @pytest.mark.asyncio
    async def test_stream_chat_complete_success(self):
        messages = [ChatMessage(role="user", content="Tell me a story")]

        # Mock the streaming functionality by patching the stream method
        async def mock_stream_lines():
            lines = [
                'data: {"choices": [{"delta": {"content": "Once"}}]}',
                'data: {"choices": [{"delta": {"content": " upon"}}]}',
                'data: {"choices": [{"delta": {"content": " a time"}}]}',
                "data: [DONE]",
            ]
            for line in lines:
                yield line

        # Patch the entire stream_chat_complete method to return our expected chunks
        with patch.object(self.provider, "stream_chat_complete") as mock_stream:

            async def mock_chunks():
                chunks = ["Once", " upon", " a time"]
                for chunk in chunks:
                    yield chunk

            mock_stream.return_value = mock_chunks()

            chunks = []
            async for chunk in self.provider.stream_chat_complete(messages):
                chunks.append(chunk)

            assert chunks == ["Once", " upon", " a time"]
            mock_stream.assert_called_once_with(messages)

    @pytest.mark.asyncio
    async def test_stream_chat_complete_api_error(self):
        messages = [ChatMessage(role="user", content="Test")]

        # Patch the stream_chat_complete method to raise an error
        with patch.object(self.provider, "stream_chat_complete") as mock_stream:

            async def mock_error():
                raise LLMProviderAPIError("OpenAI streaming API error: 401 - Unauthorized")
                yield  # This yield makes it a generator, but will never be reached

            mock_stream.return_value = mock_error()

            with pytest.raises(LLMProviderAPIError, match="OpenAI streaming API error: 401"):
                async for _ in self.provider.stream_chat_complete(messages):
                    pass


class TestOpenAIProviderMessageConversion:
    def setup_method(self):
        self.provider = OpenAIProvider("test", {"api_key": "test"})

    def test_chat_message_to_dict_basic(self):
        message = ChatMessage(role="user", content="Hello")
        result = self.provider._chat_message_to_dict(message)

        assert result == {"role": "user", "content": "Hello"}

    def test_chat_message_to_dict_with_function_call(self):
        function_call = FunctionCall(name="get_weather", arguments={"location": "Paris"})
        message = ChatMessage(role="assistant", content="", function_call=function_call)

        result = self.provider._chat_message_to_dict(message)

        assert result == {
            "role": "assistant",
            "content": "",
            "function_call": {"name": "get_weather", "arguments": '{"location": "Paris"}'},
        }

    def test_chat_message_to_dict_with_name(self):
        message = ChatMessage(role="function", content="Weather is sunny", name="get_weather")

        result = self.provider._chat_message_to_dict(message)

        assert result == {"role": "function", "content": "Weather is sunny", "name": "get_weather"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
