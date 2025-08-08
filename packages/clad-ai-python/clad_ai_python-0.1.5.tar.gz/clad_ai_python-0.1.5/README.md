# @clad-ai/python

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Python Version Support](#python-version-support)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Methods](#methods)
  - [get_processed_input](#get_processed_input)
  - [get_processed_input_fully_managed](#get_processed_input_fully_managed)
  - [get_processed_input_with_redis](#get_processed_input_with_redis)
- [Framework Integration Examples](#framework-integration-examples)
- [Error Handling](#error-handling)
- [Support](#support)

## Overview

Clad provides a lightweight **Python SDK** for secure, low-latency native ad injection in LLM workflows. Built for server-side applications, this SDK offers flexible processing modes to match your infrastructure needs.

**Key Features:**
- 🚀 **Three processing modes** for different performance and infrastructure needs
- 🐍 **Python 3.8+** support with async/await
- 🏗️ **Framework agnostic** - Works with FastAPI, Flask, Django, and more
- 🔧 **Production ready** - Built-in Redis support, error handling, and fallbacks

⚠️ This SDK is proprietary and intended for authorized Clad Labs clients only.

## Installation

```bash
pip install clad-ai-python
```

For Redis support (optional):
```bash
pip install redis
```

## Python Version Support

- **Python 3.8+**: Full support with async/await
- **Redis**: Optional dependency for production scaling

## Quick Start

```python
from clad_sdk import CladClient

# Initialize client
clad = CladClient(
    api_key="YOUR_API_KEY",
    threshold=3  # Optional: messages before triggering API (default: 3)
)

# Process user input
response = await clad.get_processed_input(
    user_input="I'm looking for running shoes",
    user_id="user-123",
    discrete="false"
)

print(response["prompt"])  # Final prompt with or without ad
```

**Configuration Parameters:**
- `api_key: str` — API key provided by Clad. Contact support@clad.ai to get yours.
- `threshold: int` — Optional. Number of messages before triggering an API call. Defaults to 3.
- `redis_client` — Optional. Redis client for `get_processed_input_with_redis` method.

## Core Concepts

✅ **Three modes of operation:**

Each mode offers a different balance of speed, memory footprint, and infrastructure requirements:

- **`get_processed_input`**: Fast with local server RAM for counting and context
- **`get_processed_input_fully_managed`**: Zero local memory, fully server-managed state  
- **`get_processed_input_with_redis`**: Production-ready with Redis for scaling across servers

## Methods

**Important:** All methods require a `user_id` parameter. In backend environments, this user ID should be passed from your frontend application (which can use the `@clad-ai/react` SDK's `getOrCreateUserId()` function). Do not generate user IDs on the backend as they will not persist across requests.

### `get_processed_input`

**Mode 1: Local Memory (Fast & Lightweight)**

Uses in-process TTL cache for ultra-fast message counting and context tracking. Ideal for single-server deployments.

```python
clad = CladClient(api_key="YOUR_API_KEY")

response = await clad.get_processed_input(
    user_input="I'm looking for shoes",
    user_id="user-123",
    discrete="false"
)
```

**Parameters:**
- `user_input: str` — User's chat input
- `user_id: str` — Persistent user ID (from frontend)
- `discrete: str` — "true" or "false" for explicit ad marking

**Returns:**
```python
{
    "prompt": str,
    "promptType": "clean" | "injected", 
    "link": str,
    "discrete": "true" | "false",
    "adType": str,
    "image_url": Optional[str]
}
```

---

### `get_processed_input_fully_managed`

**Mode 2: Zero Memory (Fully Server-Managed)**

No local memory usage. All counting and injection logic handled by Clad's backend. Adds slight network latency but requires zero local state.

```python
response = await clad.get_processed_input_fully_managed(
    user_input="Looking for cafes",
    user_id="user-123", 
    discrete="false",
    threshold=5  # Optional: override threshold
)
```

**Parameters:**
- Same as `get_processed_input`, plus:
- `threshold: int` — Optional threshold override for this request

---

### `get_processed_input_with_redis`

**Mode 3: Production-Ready (Redis-Enhanced)**

**🏆 Recommended for production environments**

Uses Redis for persistent, scalable state management. Perfect for multi-server deployments with centralized state.

```python
import redis.asyncio as aioredis

# Setup Redis
r = aioredis.from_url("redis://localhost:6379/0")
clad = CladClient(api_key="YOUR_API_KEY", redis_client=r)

# Use Redis-enhanced processing
response = await clad.get_processed_input_with_redis(
    user_input="Book a hotel",
    user_id="user-123",
    discrete="false"
)
```

**Parameters:**
Same as `get_processed_input`.

## Framework Integration Examples

### FastAPI

```python
from fastapi import FastAPI
from clad_sdk import CladClient

app = FastAPI()
clad = CladClient(api_key="YOUR_API_KEY")

@app.post("/api/chat")
async def chat(request: dict):
    message = request["message"]
    user_id = request["userId"]
    
    result = await clad.get_processed_input(message, user_id)
    
    # Send to your LLM
    llm_response = await your_llm.generate(result["prompt"])
    
    return {
        "response": llm_response,
        "hasAd": result["promptType"] == "injected"
    }
```

### Flask (with async support)

```python
from flask import Flask, request, jsonify
from clad_sdk import CladClient
import asyncio

app = Flask(__name__)
clad = CladClient(api_key="YOUR_API_KEY")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    
    # Run async function in sync context
    result = asyncio.run(clad.get_processed_input_fully_managed(
        data["message"], 
        data["userId"]
    ))
    
    return jsonify({"processedPrompt": result["prompt"]})
```

### Django (async views)

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from clad_sdk import CladClient
import json

clad = CladClient(api_key="YOUR_API_KEY")

@csrf_exempt
async def chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        
        result = await clad.get_processed_input(
            data["message"],
            data["userId"]
        )
        
        return JsonResponse({
            "prompt": result["prompt"],
            "hasAd": result["promptType"] == "injected"
        })
```

## Error Handling

The SDK provides comprehensive error handling with graceful fallbacks:

```python
# All methods return clean prompts on error
response = await clad.get_processed_input_fully_managed(message, user_id)

# Check for errors
if "_error" in response:
    print(f"API Error: {response['_error']['message']}")
    # Response still contains fallback clean prompt

# Redis method error handling
try:
    response = await clad.get_processed_input_with_redis(message, user_id)
except RuntimeError as e:
    if "Redis client not configured" in str(e):
        # Handle Redis configuration error
        pass
```

**Error Response Format:**
```python
{
    "prompt": str,        # Always present (fallback to original input)
    "promptType": "clean", # Always "clean" on error
    "link": "",           # Empty on error
    "discrete": "false",  # Default value
    "_error": {           # Present when error occurs
        "status": int,    # HTTP status code (if applicable)
        "message": str    # Error description
    }
}
```

## Support

For help, email us at [support@clad.ai](mailto:support@clad.ai)

---

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited without express written permission from Clad Labs.

© 2025 Clad Labs. All rights reserved.
