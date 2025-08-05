# Supported Providers and Models

This page lists the supported providers and their available models.

## OpenAI

- **Driver**: OpenAIModelDriver  
- **Dependencies**: ✅ openai

**Models:**

- GPT-3.5 Turbo
- GPT-4
- GPT-4 Turbo
- GPT-4o
- GPT-4o-mini

## Azure OpenAI

- **Driver**: AzureOpenAIModelDriver  
- **Dependencies**: ✅ openai

**Models:**

- GPT-4o
- GPT-4o-mini
- GPT-4 Turbo

## Anthropic

- **Driver**: OpenAIModelDriver (via OpenAI-compatible API)  
- **Dependencies**: ✅ openai

**Models:**

- Claude 3.7 Sonnet (claude-3-7-sonnet-20250219)
- Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- Claude 3.5 Haiku (claude-3-5-haiku-20241022)
- Claude 3 Opus (claude-3-opus-20240229)
- Claude 3 Haiku (claude-3-haiku-20240307)

## Z.AI

- **Driver**: ZAIModelDriver  
- **Dependencies**: ❌ zai (install with `pip install zai`)

**Models:**

- glm-4.5
- glm-4.5-air

## MoonshotAI

- **Driver**: OpenAIModelDriver (via OpenAI-compatible API)  
- **Dependencies**: ✅ openai

**Models:**

- kimi-k2-turbo-preview
- kimi-k1-8k
- kimi-k1-32k
- kimi-k1-128k

## Alibaba

- **Driver**: OpenAIModelDriver (via OpenAI-compatible API)  
- **Dependencies**: ✅ openai

**Models:**

- qwen-turbo
- qwen-plus
- qwen-max
- qwen3-coder-plus
- qwen3-coder-480b-a35b-instruct

## Google Gemini

- **Driver**: OpenAIModelDriver (via OpenAI-compatible API)  
- **Dependencies**: ✅ openai

**Models:**

- Gemini Pro
- Gemini 1.5 Pro

## DeepSeek

- **Driver**: OpenAIModelDriver (via OpenAI-compatible API)  
- **Dependencies**: ✅ openai

**Models:**

- deepseek-chat
- deepseek-coder
