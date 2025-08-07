# SpeechFlow Tests

This directory contains the test suite for the SpeechFlow library.

## Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests requiring external services
└── conftest.py     # pytest fixtures and configuration
```

## Running Tests

### All tests
```bash
uv run pytest
```

### Unit tests only
```bash
uv run pytest tests/unit/
```

### Integration tests only
```bash
uv run pytest tests/integration/
```

### With coverage
```bash
uv run pytest --cov=speechflow --cov-report=html
```

### Specific test file
```bash
uv run pytest tests/unit/test_audio_data.py
```

### Verbose output
```bash
uv run pytest -v
```

## Environment Variables

Some tests (especially integration tests) require API keys:
- `SPEECHFLOW_OPENAI_API_KEY` - OpenAI API key
- `SPEECHFLOW_GEMINI_API_KEY` - Google Gemini API key

Integration tests will be skipped if the required API keys are not available.

## Writing Tests

1. Unit tests should mock external dependencies
2. Integration tests should be marked with `@pytest.mark.integration`
3. Use fixtures from `conftest.py` when possible
4. Follow the existing test patterns