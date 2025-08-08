# How to Create a Model Provider Plugin

Model provider plugins allow you to manage model clients, connections, and other resources independently of execution environments. This guide shows you how to create model provider plugins following the standard pattern.

## The Standard Pattern

All model providers in doteval follow the same pattern:

```python
@pytest.fixture
async def client(request, model_providers):
    """Standard model provider fixture pattern."""
    handle = await model_providers.setup(request.param)
    yield handle.model
    await handle.teardown()
```

See the [Model Provider Pattern](model-provider-pattern.md) guide for detailed explanation of this pattern.

## Understanding Model Providers

Model providers handle the lifecycle of resources like:
- Model clients (API clients, local model servers)
- Database connections
- External service connections
- Shared resources that evaluations need

They are separate from runners (which handle execution environments) and are distributed as pytest fixtures.

## Creating a Custom Model Provider

### 1. Inherit from ModelProvider Base Class

All model providers MUST inherit from the `ModelProvider` base class, which enforces the standard pattern:

```python
from doteval import ModelProvider, ModelHandle
from typing import Dict, Any

class MyModelProvider(ModelProvider):
    """Custom model provider implementation."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._resources: Dict[str, Any] = {}
        self._handles: Dict[str, ModelHandle] = {}

    async def setup(self, resource_spec: str, **kwargs) -> ModelHandle:
        """Setup a resource and return a handle."""
        if resource_spec in self._handles:
            return self._handles[resource_spec]

        # Create resource (might be async)
        client = await self._create_resource(resource_spec, **kwargs)

        # Create standard handle
        handle = ModelHandle(
            resource_id=resource_spec,
            model=client,
            manager=self
        )
        self._handles[resource_spec] = handle
        self._resources[resource_spec] = client

        return handle

    async def teardown(self, resource_id: str) -> None:
        """Tear down a specific resource."""
        if resource_id in self._resources:
            client = self._resources[resource_id]
            await client.close()
            del self._resources[resource_id]
            del self._handles[resource_id]

    async def _create_resource(self, spec: str, **kwargs):
        """Create the actual resource/client."""
        # Implementation specific
        return MyClient(spec, **kwargs)
```

### 2. Example: vLLM Model Provider

Here's a complete example managing vLLM servers with single-model constraint:

```python
import asyncio
import subprocess
from typing import Dict, Optional

class VLLMProvider:
    """Manages local vLLM server instances."""

    def __init__(self, base_port: int = 8000, gpu_memory: float = 0.9):
        self.base_port = base_port
        self.gpu_memory = gpu_memory
        self._servers: Dict[str, subprocess.Popen] = {}
        self._clients: Dict[str, VLLMClient] = {}
        self._handles: Dict[str, ModelHandle] = {}
        self._next_port = base_port

    async def setup(self, model: str, **config) -> ModelHandle:
        """Setup a vLLM server and return a handle."""
        if model in self._handles:
            return self._handles[model]

        # Allocate port
        port = self._next_port
        self._next_port += 1

        # Start server
        await self._start_server(model, port, config)

        # Create handle
        handle = ModelHandle(
            resource_id=model,
            model=self._clients[model],
            manager=self
        )
        self._handles[model] = handle

        return handle

    async def teardown(self, model: str):
        """Tear down the vLLM server."""
        if model in self._servers:
            # Stop server
            self._servers[model].terminate()
            self._servers[model].wait(timeout=10)
            del self._servers[model]

            # Clean up
            if model in self._handles:
                del self._handles[model]
            if model in self._clients:
                del self._clients[model]
```

## Creating Pytest Fixtures

### 1. Required Fixtures

You must provide two fixtures following the standard pattern:

```python
# Session-scoped provider
@pytest.fixture(scope="session")
def my_model_provider(request) -> MyModelProvider:
    """Session-scoped model provider."""
    provider = MyModelProvider(config)

    # Ensure cleanup at session end
    async def cleanup():
        await provider.teardown_all()

    request.addfinalizer(lambda: asyncio.run(cleanup()))

    return provider


# Function-scoped client (THE STANDARD PATTERN)
@pytest.fixture
async def my_client(request, my_model_provider):
    """Standard model provider fixture pattern."""
    handle = await my_model_provider.setup(request.param)
    yield handle.model
    await handle.teardown()
```

## Registering Your Model Provider

### 1. Via Entry Points (Recommended)

Add your model provider to your package's `pyproject.toml`:

```toml
[project.entry-points."doteval.model_providers"]
myresource = "mypackage:my_model_provider"  # Points to fixture name

[project.entry-points.pytest11]
mypackage = "mypackage.pytest_plugin"
```

### 2. Auto-Discovery (Optional)

Users can optionally access all model providers through the `model_providers` fixture:

```python
def eval_with_discovery(model_providers):
    """Use auto-discovered model providers."""
    if "myresource" in model_providers:
        provider = model_providers["myresource"]
        handle = await provider.setup("model-name")
        try:
            # Use handle.model
        finally:
            await handle.teardown()
```

## Using Model Providers

### 1. Standard Pattern (Recommended)

```python
@pytest.mark.parametrize(
    "model_client",
    ["gpt-4", "claude-3"],
    indirect=True
)
@foreach("prompt", dataset)
async def eval_models(prompt, model_client):
    """Standard evaluation using model provider fixture."""
    response = await model_client.generate(prompt)
    return Result(response)
```

### 2. Manual Control (When Needed)

```python
@foreach("model,prompt", [
    ("gpt-4", "Hello"),
    ("claude-3", "World"),
])
async def eval_with_control(model, prompt, my_model_provider):
    """Manual resource lifecycle control."""
    handle = await my_model_provider.setup(model)
    try:
        response = await handle.model.generate(prompt)
        return Result(response)
    finally:
        await handle.teardown()
```

### 3. Application Fixtures

Create higher-level fixtures that use model providers:

```python
@pytest.fixture
def application(request, vllm_provider):
    """Application fixture using model provider."""
    model = request.param
    client = vllm_provider.get_client(model)

    class Application:
        def __init__(self, client):
            self.client = client

        def process(self, text):
            # Application logic using client
            return self.client.generate(text)

    return Application(client)


@pytest.mark.parametrize(
    "application",
    ["llama-7b", "mistral-7b"],
    indirect=True
)
@foreach("task", tasks)
def eval_application(task, application):
    result = application.process(task)
    return Result(result)
```

## Best Practices

### 1. Resource Caching

Cache expensive resources to avoid recreation:

```python
class CachingManager:
    def __init__(self):
        self._cache = {}
        self._lock = asyncio.Lock()

    async def get_client(self, **kwargs):
        key = self._make_key(kwargs)

        async with self._lock:
            if key not in self._cache:
                self._cache[key] = await self._create_client(**kwargs)

        return self._cache[key]
```

### 2. Configuration Management

Support both CLI options and direct configuration:

```python
@pytest.fixture(scope="session")
def my_manager(request):
    """Flexible configuration."""
    # Check for CLI options
    if hasattr(request, "config"):
        url = request.config.getoption("--api-url", "http://localhost")
    else:
        url = "http://localhost"

    return MyManager(url)
```

### 3. Error Handling

Handle resource creation failures gracefully:

```python
async def setup(self, spec: str) -> ResourceHandle:
    """Setup with error handling."""
    try:
        client = await self._create_resource(spec)
        # ... create handle
    except Exception as e:
        # Log error and provide helpful message
        raise RuntimeError(
            f"Failed to setup resource '{spec}': {e}\n"
            f"Ensure the service is running and accessible."
        )
```

### 4. Lifecycle Documentation

Document resource lifecycle clearly:

```python
class MyManager:
    """Resource manager for X service.

    Lifecycle:
    - Resources are created on first request (lazy)
    - Resources are cached and reused
    - Call shutdown() to clean up all resources

    Thread-safety:
    - get_client() is thread-safe
    - setup/teardown operations are async-safe
    """
```

## Implementation Checklist

When implementing a model provider:

- [ ] Return a `ModelHandle` from `setup()` with `model` attribute and `teardown()` method
- [ ] Implement `setup()` method returning a handle
- [ ] Implement `teardown()` method for cleanup
- [ ] Provide session-scoped provider fixture
- [ ] Provide function-scoped client fixture following the standard pattern
- [ ] Document resource constraints (e.g., single model for vLLM)

## Common Pitfalls to Avoid

### Don't: Multiple Patterns

```python
# Bad - confusing multiple ways to do the same thing
class Provider:
    def get_client(self, model): ...  # Old pattern
    async def setup(self, model): ...  # New pattern
    async def create(self, model): ... # Another pattern?
```

### Do: One Clear Pattern

```python
# Good - one way to do things
class Provider:
    async def setup(self, model) -> ResourceHandle:
        """The only way to create resources."""
        ...
```

## Conclusion

The handle pattern provides a consistent, explicit approach to resource management:

1. **One Pattern**: All model providers use `setup()` → handle → `teardown()`
2. **Explicit Lifecycle**: Users see exactly when resources are created/destroyed
3. **Natural Fixtures**: Standard pytest fixture pattern with setup/teardown
4. **Flexible**: Works for any resource type
5. **Testable**: Easy to mock and test

See the [Model Provider Pattern](model-provider-pattern.md) guide for the complete pattern specification.
