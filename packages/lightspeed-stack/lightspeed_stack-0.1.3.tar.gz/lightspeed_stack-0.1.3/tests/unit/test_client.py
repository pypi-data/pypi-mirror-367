"""Unit tests for functions defined in src/client.py."""

import pytest

from client import LlamaStackClientHolder, AsyncLlamaStackClientHolder
from models.config import LlamaStackConfiguration


def test_client_get_client_method() -> None:
    """Test how get_client method works for uninitialized client."""

    client = LlamaStackClientHolder()

    with pytest.raises(
        RuntimeError,
        match="LlamaStackClient has not been initialised. Ensure 'load\\(..\\)' has been called.",
    ):
        client.get_client()


def test_async_client_get_client_method() -> None:
    """Test how get_client method works for uninitialized client."""
    client = AsyncLlamaStackClientHolder()

    with pytest.raises(
        RuntimeError,
        match=(
            "AsyncLlamaStackClient has not been initialised. "
            "Ensure 'load\\(..\\)' has been called."
        ),
    ):
        client.get_client()


def test_get_llama_stack_library_client() -> None:
    """Test if Llama Stack can be initialized in library client mode."""
    cfg = LlamaStackConfiguration(
        url=None,
        api_key=None,
        use_as_library_client=True,
        library_client_config_path="./tests/configuration/minimal-stack.yaml",
    )
    client = LlamaStackClientHolder()
    client.load(cfg)
    assert client is not None

    ls_client = client.get_client()
    assert ls_client is not None
    assert not ls_client.is_closed()
    ls_client.close()
    assert ls_client.is_closed()


def test_get_llama_stack_remote_client() -> None:
    """Test if Llama Stack can be initialized in remove client (server) mode."""
    cfg = LlamaStackConfiguration(
        url="http://localhost:8321",
        api_key=None,
        use_as_library_client=False,
        library_client_config_path="./tests/configuration/minimal-stack.yaml",
    )
    client = LlamaStackClientHolder()
    client.load(cfg)
    assert client is not None

    ls_client = client.get_client()
    assert ls_client is not None
    assert not ls_client.is_closed()
    ls_client.close()
    assert ls_client.is_closed()


def test_get_llama_stack_wrong_configuration() -> None:
    """Test if configuration is checked before Llama Stack is initialized."""
    cfg = LlamaStackConfiguration(
        url=None,
        api_key=None,
        use_as_library_client=True,
        library_client_config_path="./tests/configuration/minimal-stack.yaml",
    )
    cfg.library_client_config_path = None
    with pytest.raises(
        Exception,
        match="Configuration problem: library_client_config_path option is not set",
    ):
        client = LlamaStackClientHolder()
        client.load(cfg)


@pytest.mark.asyncio
async def test_get_async_llama_stack_library_client() -> None:
    """Test the initialization of asynchronous Llama Stack client in library mode."""
    cfg = LlamaStackConfiguration(
        url=None,
        api_key=None,
        use_as_library_client=True,
        library_client_config_path="./tests/configuration/minimal-stack.yaml",
    )
    client = AsyncLlamaStackClientHolder()
    await client.load(cfg)
    assert client is not None

    async with client.get_client() as ls_client:
        assert ls_client is not None
        assert not ls_client.is_closed()
        await ls_client.close()
        assert ls_client.is_closed()


async def test_get_async_llama_stack_remote_client() -> None:
    """Test the initialization of asynchronous Llama Stack client in server mode."""
    cfg = LlamaStackConfiguration(
        url="http://localhost:8321",
        api_key=None,
        use_as_library_client=False,
        library_client_config_path="./tests/configuration/minimal-stack.yaml",
    )
    client = AsyncLlamaStackClientHolder()
    await client.load(cfg)
    assert client is not None

    ls_client = client.get_client()
    assert ls_client is not None


async def test_get_async_llama_stack_wrong_configuration() -> None:
    """Test if configuration is checked before Llama Stack is initialized."""
    cfg = LlamaStackConfiguration(
        url=None,
        api_key=None,
        use_as_library_client=True,
        library_client_config_path="./tests/configuration/minimal-stack.yaml",
    )
    cfg.library_client_config_path = None
    with pytest.raises(
        Exception,
        match="Configuration problem: library_client_config_path option is not set",
    ):
        client = AsyncLlamaStackClientHolder()
        await client.load(cfg)
