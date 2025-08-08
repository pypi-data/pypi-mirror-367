# How to Create an Evaluator Plugin

Evaluator plugins allow you to create reusable evaluation functions that can be distributed and shared across projects. This guide shows you how to create evaluator plugins using the `@evaluator` decorator pattern.

## Understanding Evaluators

Evaluators in doteval are functions that:
- Compare model outputs against expected results
- Return boolean values or scores
- Are wrapped with the `@evaluator` decorator to produce `Score` objects
- Can be simple exact matches or complex LLM-based judgments

## The @evaluator Decorator

The `@evaluator` decorator transforms regular functions into evaluators that return `Score` objects with associated metrics:

```python
from doteval.evaluators import evaluator
from doteval.metrics import accuracy

@evaluator(metrics=accuracy())
def exact_match(result, expected, name=None):
    """Simple exact match evaluator."""
    return result == expected
```

### Key Features

1. **Automatic Score Creation**: The decorator wraps your function to return a `Score` object
2. **Metric Association**: Specify one or more metrics to calculate
3. **Metadata Tracking**: Function arguments are captured as metadata
4. **Custom Naming**: Optional `name` parameter for custom score names

## Creating Custom Evaluators

### 1. Simple String Matching

```python
from doteval.evaluators import evaluator
from doteval.metrics import accuracy

@evaluator(metrics=accuracy())
def case_insensitive_match(result, expected, name=None):
    """Case-insensitive string comparison."""
    return str(result).lower() == str(expected).lower()

@evaluator(metrics=accuracy())
def contains_match(result, expected, name=None):
    """Check if expected value is contained in result."""
    return str(expected) in str(result)
```

### 2. Numeric Evaluators

```python
@evaluator(metrics=accuracy())
def within_tolerance(result, expected, tolerance=0.1, name=None):
    """Check if numeric result is within tolerance of expected."""
    try:
        result_num = float(result)
        expected_num = float(expected)
        return abs(result_num - expected_num) <= tolerance
    except (ValueError, TypeError):
        return False
```

### 3. LLM-Based Evaluators

Create sophisticated evaluators using language models:

```python
from typing import Optional
from doteval.evaluators import evaluator
from doteval.metrics import accuracy

@evaluator(metrics=accuracy())
def semantic_similarity(
    result: str,
    expected: str,
    model_client,  # Injected by pytest fixture
    threshold: float = 0.8,
    name: Optional[str] = None
) -> bool:
    """Evaluate semantic similarity using LLM embeddings."""
    # Get embeddings
    result_embedding = model_client.get_embedding(result)
    expected_embedding = model_client.get_embedding(expected)

    # Calculate cosine similarity
    import numpy as np
    similarity = np.dot(result_embedding, expected_embedding) / (
        np.linalg.norm(result_embedding) * np.linalg.norm(expected_embedding)
    )

    return float(similarity) >= threshold
```

## Creating an Evaluator Plugin Package

### 1. Project Structure

```
my-evaluators/
├── pyproject.toml
├── README.md
├── src/
│   └── my_evaluators/
│       ├── __init__.py
│       ├── evaluators.py
│       └── llm_evaluators.py
└── tests/
    └── test_evaluators.py
```

### 2. Package Configuration

Create `pyproject.toml`:

```toml
[project]
name = "my-evaluators"
version = "0.1.0"
description = "Custom evaluators for doteval"
dependencies = [
    "doteval>=0.1.0",
    "numpy>=1.20.0",  # If using embeddings
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
]

# Optional: Register as pytest plugin for auto-discovery
[project.entry-points.pytest11]
my_evaluators = "my_evaluators"
```

### 3. Implementation Example

`src/my_evaluators/evaluators.py`:

```python
"""Custom evaluators for domain-specific evaluation."""

from typing import Any, Optional
from doteval.evaluators import evaluator
from doteval.metrics import accuracy, precision

@evaluator(metrics=accuracy())
def code_syntax_valid(result: str, language: str = "python", name: Optional[str] = None) -> bool:
    """Check if code has valid syntax."""
    if language == "python":
        try:
            compile(result, "<string>", "exec")
            return True
        except SyntaxError:
            return False
    # Add more languages as needed
    raise ValueError(f"Unsupported language: {language}")

@evaluator(metrics=[accuracy(), precision()])
def json_structure_match(result: str, expected_keys: list, name: Optional[str] = None) -> bool:
    """Check if JSON result contains expected keys."""
    import json
    try:
        data = json.loads(result)
        if not isinstance(data, dict):
            return False
        return all(key in data for key in expected_keys)
    except json.JSONDecodeError:
        return False

@evaluator(metrics=accuracy())
def response_quality(
    response: str,
    min_length: int = 10,
    max_length: int = 1000,
    required_phrases: Optional[list] = None,
    name: Optional[str] = None
) -> bool:
    """Evaluate response quality based on multiple criteria."""
    # Check length constraints
    if not (min_length <= len(response) <= max_length):
        return False

    # Check required phrases
    if required_phrases:
        response_lower = response.lower()
        if not all(phrase.lower() in response_lower for phrase in required_phrases):
            return False

    return True
```

### 4. LLM-Based Evaluator Plugin

`src/my_evaluators/llm_evaluators.py`:

```python
"""LLM-based evaluators for sophisticated evaluation tasks."""

from typing import Optional
from doteval.evaluators import evaluator
from doteval.metrics import accuracy

@evaluator(metrics=accuracy())
def llm_judge(
    result: str,
    expected: str,
    model_client,  # Injected via pytest fixture
    criteria: str = "Is the result correct and appropriate?",
    temperature: float = 0,
    name: Optional[str] = None
) -> bool:
    """Use an LLM to judge if the result meets criteria."""
    prompt = f"""You are an expert evaluator. Evaluate if the result meets the criteria.

Criteria: {criteria}
Expected: {expected}
Actual Result: {result}

Respond with only 'true' or 'false'."""

    response = model_client.generate(
        prompt=prompt,
        temperature=temperature,
        max_tokens=10
    )

    return response.strip().lower() == "true"

@evaluator(metrics=accuracy())
def factual_consistency(
    result: str,
    reference: str,
    model_client,
    name: Optional[str] = None
) -> bool:
    """Check if result is factually consistent with reference."""
    prompt = f"""Determine if the text is factually consistent with the reference.

Reference: {reference}
Text to verify: {result}

Is the text factually consistent? Reply 'true' or 'false' only."""

    response = model_client.generate(prompt=prompt, temperature=0)
    return response.strip().lower() == "true"
```

## Using Evaluator Plugins

### 1. Direct Import

```python
from my_evaluators import code_syntax_valid, json_structure_match
from doteval import foreach

@foreach("code,language", [
    ("print('hello')", "python"),
    ("console.log('hello')", "javascript"),
])
def eval_code_generation(code, language, model_client):
    result = model_client.generate(f"Fix this code: {code}")
    return code_syntax_valid(result, language)
```

### 2. With Model Providers

```python
from my_evaluators.llm_evaluators import llm_judge
from doteval import foreach

@pytest.mark.parametrize("model_client", ["gpt-4"], indirect=True)
@foreach("prompt,expected", dataset)
def eval_responses(prompt, expected, model_client):
    result = model_client.generate(prompt)
    return llm_judge(
        result,
        expected,
        model_client,
        criteria="Is the response helpful and accurate?"
    )
```

### 3. Composing Multiple Evaluators

```python
from my_evaluators import response_quality, factual_consistency
from doteval import foreach
from doteval.models import Result

@foreach("question,reference", qa_dataset)
def eval_qa_comprehensive(question, reference, model_client):
    response = model_client.generate(question)

    # Apply multiple evaluators
    quality_check = response_quality(
        response,
        min_length=50,
        required_phrases=["because", "therefore"]
    )

    factual_check = factual_consistency(
        response,
        reference,
        model_client
    )

    # Return combined result
    return Result(
        success=quality_check and factual_check,
        metrics={
            "quality": quality_check,
            "factual": factual_check
        }
    )
```

## Best Practices

### 1. Parameter Design

Make evaluators flexible with sensible defaults:

```python
@evaluator(metrics=accuracy())
def flexible_match(
    result: str,
    expected: str,
    ignore_case: bool = True,
    ignore_whitespace: bool = True,
    partial_match: bool = False,
    name: Optional[str] = None
) -> bool:
    """Flexible string matching with options."""
    # Process based on options
    if ignore_case:
        result = result.lower()
        expected = expected.lower()

    if ignore_whitespace:
        result = result.strip()
        expected = expected.strip()

    if partial_match:
        return expected in result
    else:
        return result == expected
```

### 2. Error Handling

Handle edge cases gracefully:

```python
@evaluator(metrics=accuracy())
def safe_json_match(result: Any, expected_structure: dict, name: Optional[str] = None) -> bool:
    """Safely evaluate JSON structure."""
    if result is None:
        return False

    # Handle various input types
    if isinstance(result, str):
        try:
            import json
            result = json.loads(result)
        except json.JSONDecodeError:
            return False

    # Validate structure
    # ... validation logic
```

### 3. Documentation

Document evaluator behavior clearly:

```python
@evaluator(metrics=accuracy())
def domain_specific_match(result: str, expected: str, name: Optional[str] = None) -> bool:
    """Evaluate domain-specific outputs.

    This evaluator checks for:
    1. Correct format (e.g., "ANSWER: <value>")
    2. Semantic equivalence for the value
    3. Proper capitalization of keywords

    Args:
        result: Model output to evaluate
        expected: Expected answer format
        name: Optional custom name for the score

    Returns:
        True if result matches domain-specific criteria

    Examples:
        >>> domain_specific_match("ANSWER: 42", "ANSWER: 42")
        True
        >>> domain_specific_match("answer: 42", "ANSWER: 42")
        False  # Wrong capitalization
    """
    # Implementation...
```

### 4. Testing Your Evaluators

Always test your evaluators:

```python
# tests/test_evaluators.py
import pytest
from my_evaluators import code_syntax_valid, flexible_match

def test_code_syntax_valid():
    # Valid Python code
    assert code_syntax_valid("print('hello')", "python") == True

    # Invalid Python code
    assert code_syntax_valid("print('hello'", "python") == False

    # Unsupported language
    with pytest.raises(ValueError):
        code_syntax_valid("code", "unsupported")

def test_flexible_match():
    # Test various options
    assert flexible_match("Hello", "hello", ignore_case=True) == True
    assert flexible_match("Hello", "hello", ignore_case=False) == False
    assert flexible_match("Hello World", "World", partial_match=True) == True
```

## Advanced Patterns

### 1. Stateful Evaluators

For evaluators that need to maintain state:

```python
class StatefulEvaluator:
    def __init__(self):
        self.history = []

    @evaluator(metrics=accuracy())
    def consistency_check(self, result: str, expected: str, name: Optional[str] = None) -> bool:
        """Check consistency with previous responses."""
        # Store current response
        self.history.append(result)

        # Check consistency logic
        if len(self.history) > 1:
            # Compare with previous responses
            # ... consistency logic
            pass

        return result == expected

# Usage
evaluator_instance = StatefulEvaluator()

@foreach("prompt,expected", dataset)
def eval_consistency(prompt, expected, model_client):
    result = model_client.generate(prompt)
    return evaluator_instance.consistency_check(result, expected)
```

### 2. Multi-Metric Evaluators

Return multiple metrics from one evaluation:

```python
from doteval.metrics import accuracy, precision, recall

@evaluator(metrics=[accuracy(), precision(), recall()])
def multi_label_match(result: list, expected: list, name: Optional[str] = None) -> bool:
    """Evaluate multi-label classification."""
    result_set = set(result)
    expected_set = set(expected)

    # For the boolean return, check exact match
    # Individual metrics will calculate precision/recall
    return result_set == expected_set
```

## Conclusion

Evaluator plugins provide a powerful way to:

1. **Encapsulate Domain Logic**: Create evaluators specific to your use case
2. **Promote Reusability**: Share evaluators across projects
3. **Ensure Consistency**: Standardize evaluation criteria
4. **Enable Composition**: Combine multiple evaluators for comprehensive evaluation

Start with simple evaluators and progressively add sophistication as needed. The `@evaluator` decorator pattern makes it easy to create, test, and distribute your custom evaluation logic.
