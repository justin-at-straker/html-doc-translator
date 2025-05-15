# HTML Translation Service

A FastAPI microservice that translates HTML content while preserving structure, with pluggable translation providers.

## Features

- Translate HTML content while maintaining the original structure
- Pluggable translation provider system (currently supports Google Cloud Translation and OpenAI)
- Easy to extend with additional translation providers
- REST API with OpenAPI documentation

## Requirements

- Python 3.9+
- For Google Cloud Translation:
  - A Google Cloud Platform account
  - A project with the Translation API enabled
  - Service account credentials
- For OpenAI:
  - An OpenAI API key

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/html-translate.git
cd html-translate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Required for Google Cloud Translation
GCP_PROJECT_ID=your-google-cloud-project-id
GCP_LOCATION=global
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Required for OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo # Optional, defaults to gpt-3.5-turbo

# Choose which translation provider to use
TRANSLATION_PROVIDER=google # or openai, or dummy for testing
```

## Usage

### Starting the server

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### API Endpoints

- `GET /` - Service information
- `GET /api/v1/health` - Health check
- `POST /api/v1/translate` - Translate HTML content

### API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Adding New Translation Providers

To add a new translation provider:

1. Create a new file in the `providers` directory, e.g., `providers/new_provider.py`
2. Implement a class that inherits from `TranslationProvider` (implementing `translate_batch` and optionally `translate_batch_async`)
3. Add your provider to the factory in `providers/factory.py`

Example:

```python
# providers/azure.py
from providers.base import TranslationProvider

class AzureTranslationProvider(TranslationProvider):
    def translate_batch(self, texts, target_lang, source_lang=None):
        # Azure implementation here
        pass
```

Then update the factory:

```python
# In providers/factory.py
elif settings.translation_provider.lower() == "azure":
    return AzureTranslationProvider()
elif settings.translation_provider.lower() == "openai":
    return OpenAITranslationProvider()
elif settings.translation_provider.lower() == "dummy":
    return DummyTranslationProvider()
```

## License

MIT 