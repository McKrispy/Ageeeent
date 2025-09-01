# Environment Variable Setup Guide

## 1. Create .env file

Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

## 2. Edit .env file

Fill in your actual API keys in the `.env` file:

```bash
# API Keys
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
GOOGLE_CLOUD_API_KEY=your-actual-google-cloud-api-key-here
GOOGLE_CLOUD_PROJECT_ID=your-actual-project-id-here

# Other configurations...
```

## 3. Install dependencies (optional)

If you want to use the `python-dotenv` library to automatically load .env files:

```bash
pip install python-dotenv
```

## 4. Usage in code

### Method 1: Using python-dotenv (recommended)

```python
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get environment variables
api_key = os.getenv('OPENAI_API_KEY')
```

### Method 2: Direct use of os.environ

```python
import os

# Directly get environment variables
api_key = os.getenv('OPENAI_API_KEY')
```

## 5. Usage in LLM interface

```python
from Interfaces.llm_api_interface import OpenAIInterface, GoogleCloudInterface

# Create interface instances (will automatically get API keys from environment variables)
openai_interface = OpenAIInterface()
google_interface = GoogleCloudInterface()
```

## 6. Security considerations

- `.env` file has been added to `.gitignore` and will not be committed to version control
- Never hardcode API keys in code
- In production environments, recommend using more secure environment variable management methods