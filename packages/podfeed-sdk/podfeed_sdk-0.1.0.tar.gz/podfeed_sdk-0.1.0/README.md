# PodFeed SDK

A Python SDK for the PodFeed API, enabling developers to generate high-quality Podcast-style audio content from various input sources using AI.

## Features

- **Multiple Input Types**: Support for text, URLs, files, topics, and bring-your-own-script
- **Audio Generation Modes**: Monologue (single voice) and dialogue (two voices) modes
- **Voice Customization**: Multiple voice options for different languages. Some voices support custom instructions
- **Script Customization**: Adjustable complexity levels, lengths, and emphasis


## Installation

```bash
pip install podfeed-sdk
```

To install in editable (developer) mode: 
```bash
python3 -m venv venv
. venv/bin/activate 

pip install -e podfeed
```

## Authentication

The SDK supports two ways to provide your API key:

1. **Environment Variable**:
   ```bash
   export PODFEED_API_KEY="your-api-key-here"
   ```

2. **Direct initialization**:
   ```python
   from podfeed import PodfeedClient
   
   client = PodfeedClient(api_key="your-api-key-here")
   ```

## Quick Start


### Get an API key

**Temporary Solution**
1. Login to tst.podfeed.ai, get JWT token from Browser
2. Run:

```python
import requests 

URL = "https://podfeed-tst-gateway-deulhl0f.uc.gateway.dev"
api_key_request = {
    "name": "Test key",
    "description": "Test key"
}
access_token = PASTE_YOUR_ACCESS_TOKEN_HERE
api_key_response = requests.post(f"{URL}/api/api-keys/create", headers={"Authorization": f"Bearer {access_token}"},json=api_key_request)
print(api_key_response.json())
```

---

### Generate Audio (from Website)

```python
from podfeed import (
    PodfeedClient,
    PodfeedError,
    AudioGenerationRequest,
    InputContent,
    VoiceConfig,
    ContentConfig,
)

# Initialize client (uses PODFEED_API_KEY env var)
client = PodfeedClient()

# Example URL
website_url = "https://podfeed.ai/faq"

# Generate audio from website
result = client.generate_audio(
    request=AudioGenerationRequest(
        input_type="url",
        mode="dialogue",
        input_content=InputContent(url=website_url),
        voice_config=VoiceConfig(
            host_voice="google-male-puck", cohost_voice="google-female-leda"
        ),
        content_config=ContentConfig(
            level="intermediate",
            length="medium",
            language="en-US",
        ),
    )
)

task_id = response["task_id"]
print(f"Task created: {task_id}")

# Wait for completion
result = client.wait_for_completion(task_id)
print(f"Audio generated: {result['result']['audio_url']}")
```

### List Available Voices

```python
from podfeed import PodfeedClient

api_key = os.getenv("PODFEED_API_KEY")
if not api_key:
    print("Error: PODFEED_API_KEY environment variable not set")
    return 1

client = PodfeedClient(api_key=api_key)

voices_config = client.list_available_voices()
print(voices_config)
```

## Usage Examples
See `examples` directory.

## Error Handling

```python
from podfeed_sdk import PodfeedClient, PodfeedError, PodfeedAuthError, PodfeedAPIError

try:
    client = PodfeedClient()
    response = client.generate_audio(
        input_type="text",
        text_content="Sample text"
    )
except PodFeedAuthError as e:
    print(f"Authentication error: {e}")
except PodFeedAPIError as e:
    print(f"API error: {e.message} (Status: {e.status_code})")
except PodFeedError as e:
    print(f"General error: {e}")
```

## API Reference

### Core Methods

- `generate_audio(**kwargs)` - Generate audio from various input types
- `wait_for_completion(task_id, timeout=1800)` - Wait for task completion
- `get_task_progress(task_id)` - Check task progress
- `get_audio_status(task_id)` - Get audio generation status

### Audio Management

- `list_audios(limit=20, offset=0, status=None)` - List audio files
- `get_audio(audio_id)` - Get audio details
- `delete_audio(audio_id)` - Delete audio file
- `download_audio_with_metadata(audio_id)` - Download with metadata

### File Operations

- `get_upload_urls(files)` - Get signed upload URLs
- `create_share_link(audio_id)` - Create shareable link

### Account

- `get_account_usage()` - Get usage statistics

## Requirements

- Python 3.7+
- requests >= 2.25.0

## Rate Limits
TODO

## Support

For API support, email support@podfeed.ai.