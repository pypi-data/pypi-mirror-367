# Plugin Architecture

doteval's plugin architecture enables extensibility across all major components of the evaluation framework. This document explains the design philosophy, implementation details, and how different plugin types work together.

## Overview

The plugin system in doteval is built on three core principles:

1. **Extensibility**: Every major component can be extended or replaced
2. **Discoverability**: Plugins are automatically discovered and integrated
3. **Consistency**: All plugins follow standardized patterns and interfaces

## Plugin Types

doteval supports five main types of plugins:

### 1. Model Provider Plugins

Model providers manage the lifecycle of model clients and resources. They handle:
- Model server initialization (e.g., vLLM, TGI)
- API client management (e.g., OpenAI, Anthropic)
- Resource pooling and cleanup
- Connection management

**Key Components:**
- Base class: `ModelProvider`
- Handle pattern: `ModelHandle` for resource lifecycle
- Discovery: `doteval.model_providers` entry point
- Examples: `doteval-vllm`, custom API providers

### 2. Evaluator Plugins

Evaluators define how to compare model outputs with expected results. They provide:
- Evaluation logic (exact match, semantic similarity, etc.)
- Metric association
- LLM-based judgment capabilities
- Domain-specific evaluation criteria

**Key Components:**
- Decorator: `@evaluator`
- Return type: `Score` objects with metrics
- Discovery: Direct import or package distribution
- Examples: `doteval-evaluators-llm`, custom evaluators

### 3. Runner Plugins

Runners orchestrate evaluation execution across different environments:
- Local execution (default)
- Distributed execution (Modal, Ray)
- Cloud platforms (SageMaker, Vertex AI)
- Custom infrastructure

**Key Components:**
- Base class: `Runner`
- Entry point: `doteval.runners`
- Integration: Deep pytest integration
- Examples: `doteval-modal`, `doteval-sagemaker`

### 4. Storage Plugins

Storage backends persist evaluation results:
- JSON files (default)
- SQLite databases
- Cloud storage (S3, GCS)
- Custom databases

**Key Components:**
- Base class: `Storage`
- URL scheme: Protocol-based selection
- Methods: `create_experiment`, `add_results`, etc.
- Examples: `doteval-storage-sqlite`

### 5. Dataset Plugins

Dataset plugins provide access to evaluation datasets:
- Standard benchmarks (GSM8K, MMLU, etc.)
- Custom datasets
- Dynamic data loading
- Multi-format support

**Key Components:**
- Base class: `Dataset`
- Registry: Dynamic attribute access via `foreach.<dataset>`
- Discovery: Registration at import
- Examples: `doteval-datasets`

## Plugin Discovery Mechanisms

### 1. Python Entry Points

The primary discovery mechanism for most plugins:

```toml
# pyproject.toml
[project.entry-points."doteval.model_providers"]
my_provider = "my_package:provider_fixture_name"

[project.entry-points."doteval.runners"]
my_runner = "my_package:MyRunnerClass"

[project.entry-points.pytest11]
my_plugin = "my_package.pytest_plugin"
```

Entry points enable:
- Automatic discovery on package installation
- No manual registration required
- Clean separation of concerns
- Multiple plugins per package

### 2. Registry Pattern

Used for datasets and runtime registration:

```python
# Datasets use a global registry
from doteval.datasets.base import Dataset, _registry

@dataclass
class MyDataset(Dataset):
    name = "mydataset"
    columns = ["input", "output"]

_registry.register(MyDataset)

# Usage via dynamic attributes
@foreach.mydataset(split="test")
def evaluate(input, output):
    # ...
```

### 3. URL-Based Configuration

Storage backends use URL schemes:

```python
# Automatically selects appropriate backend
storage = get_storage("sqlite:///results.db")
storage = get_storage("s3://bucket/path")
storage = get_storage("json://./results")
```

## Integration with pytest

doteval deeply integrates with pytest's plugin system:

### 1. Collection Phase

```python
@pytest.hookimpl
def pytest_collection_modifyitems(config, items):
    """Mark all @foreach decorated functions as doteval items."""
    for item in items:
        if hasattr(item.function, "_foreach_decorator"):
            item.add_marker(pytest.mark.doteval)
```

### 2. Execution Control

```python
@pytest.hookimpl
def pytest_runtest_call(item):
    """Defer doteval function execution to session end."""
    if item.get_closest_marker("doteval"):
        # Store for later execution
        config._doteval_items.append(item)
        return None  # Skip normal execution
```

### 3. Session Finish

```python
@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Execute all doteval items with appropriate runner."""
    runner = get_runner(session.config)
    asyncio.run(runner.run_evaluations(config._doteval_items))
```

## Plugin Communication

Plugins communicate through well-defined interfaces:

### 1. Fixture Injection

Model providers are injected as pytest fixtures:

```python
@pytest.mark.parametrize("model_client", ["gpt-4"], indirect=True)
@foreach("prompt", prompts)
def evaluate(prompt, model_client):
    # model_client is injected by the model provider
    response = model_client.generate(prompt)
    return exact_match(response, expected)
```

### 2. Runner Context

Runners provide execution context to evaluations:

```python
class Runner:
    async def run_evaluations(self, items):
        async with self.setup_context():
            for item in items:
                result = await self.execute_item(item)
                self.storage.add_result(result)
```

### 3. Storage Interface

All storage backends implement the same interface:

```python
class Storage(ABC):
    @abstractmethod
    def create_experiment(self, name: str) -> Experiment:
        pass

    @abstractmethod
    def add_results(self, experiment: str, results: List[Record]):
        pass
```

## Design Benefits

### 1. Separation of Concerns

Each plugin type has a specific responsibility:
- **Model Providers**: Resource management
- **Evaluators**: Evaluation logic
- **Runners**: Execution orchestration
- **Storage**: Result persistence
- **Datasets**: Data access

### 2. Composability

Plugins can be mixed and matched:

```python
# Use Modal runner with vLLM provider and SQLite storage
pytest.main([
    "--runner=modal",
    "--model-provider=vllm",
    "--storage=sqlite:///results.db",
    "eval_script.py"
])
```

### 3. Progressive Complexity

Start simple and add plugins as needed:

```python
# Simple: Local execution with default storage
@foreach("q,a", questions)
def eval_simple(q, a):
    return exact_match(generate(q), a)

# Complex: Distributed execution with custom everything
@pytest.mark.parametrize("vllm_client", ["llama-70b"], indirect=True)
@foreach.custom_dataset(split="hard")
@modal_runner.remote
def eval_complex(question, answer, vllm_client):
    response = vllm_client.generate(question)
    return llm_judge(response, answer, criteria="...")
```

## Creating Plugin Packages

### 1. Package Structure

Standard structure for plugin packages:

```
my-doteval-plugin/
├── pyproject.toml          # Package metadata and entry points
├── README.md               # Documentation
├── src/
│   └── my_plugin/
│       ├── __init__.py
│       ├── plugin.py       # Main plugin code
│       └── pytest_plugin.py # pytest integration
└── tests/
    └── test_plugin.py
```

### 2. Entry Point Registration

Register your plugin for discovery:

```toml
[project.entry-points."doteval.model_providers"]
my_provider = "my_plugin:my_provider_fixture"

[project.entry-points.pytest11]
my_plugin = "my_plugin.pytest_plugin"
```

### 3. Testing Plugins

Test plugins in isolation and integration:

```python
# Unit test
def test_my_evaluator():
    score = my_evaluator("result", "expected")
    assert score.value == True

# Integration test
def test_with_doteval(tmp_path):
    result = pytest.main([
        "--experiment=test",
        "test_evaluation.py"
    ])
    assert result == 0
```

## Best Practices

### 1. Follow Established Patterns

Each plugin type has established patterns:

```python
# Model Provider Pattern
class MyProvider(ModelProvider):
    async def setup(self, spec: str) -> ModelHandle:
        # Return handle with .model and .teardown()

# Evaluator Pattern
@evaluator(metrics=accuracy())
def my_evaluator(result, expected):
    # Return boolean
```

### 2. Handle Errors Gracefully

Provide helpful error messages:

```python
def setup(self, model_spec: str):
    if not self.is_available():
        raise RuntimeError(
            f"MyProvider requires X to be installed.\n"
            f"Install with: pip install my-provider[required]"
        )
```

### 3. Document Plugin Behavior

Clear documentation helps users:

```python
class MyRunner(Runner):
    """Execute evaluations on custom infrastructure.

    This runner requires:
    - Environment variable MY_API_KEY
    - Network access to infrastructure

    Configuration:
    - max_workers: Maximum parallel evaluations (default: 10)
    - timeout: Evaluation timeout in seconds (default: 300)
    """
```

### 4. Version Compatibility

Specify compatible versions:

```toml
[project]
dependencies = [
    "doteval>=0.1.0,<1.0",  # Compatible with 0.x
]
```

## Plugin Lifecycle

### 1. Discovery Phase

1. Python imports the package
2. Entry points are registered
3. Plugin hooks are installed

### 2. Initialization Phase

1. pytest configures with plugin
2. Fixtures are registered
3. Resources are prepared

### 3. Execution Phase

1. Evaluations request resources
2. Plugins provide functionality
3. Results are collected

### 4. Cleanup Phase

1. Resources are released
2. Results are persisted
3. Cleanup hooks run

## Future Extensibility

The plugin architecture is designed for future expansion:

### Potential Plugin Types

1. **Preprocessor Plugins**: Transform data before evaluation
2. **Metric Plugins**: Custom evaluation metrics
3. **Reporter Plugins**: Custom result formatting
4. **Cache Plugins**: Result caching strategies

### Extension Points

The architecture provides hooks for:
- Custom pytest markers
- Evaluation lifecycle events
- Result post-processing
- Custom CLI commands

## Conclusion

doteval's plugin architecture provides:

1. **Flexibility**: Extend any component
2. **Simplicity**: Use only what you need
3. **Consistency**: Predictable patterns
4. **Community**: Share and reuse plugins

This design enables doteval to serve both simple evaluation scripts and complex production pipelines while maintaining a consistent, pythonic interface throughout.
