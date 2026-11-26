# Straitly Model Provider for Dify

Model provider plugin for [Straitly](https://straitly.ai), an AI gateway with one OpenAI-compatible API key for 150+ models including Claude, GPT, Gemini, Grok and DeepSeek.

## Supported Models

| Model ID | Context | Input | Capabilities |
| --- | --- | --- | --- |
| `claude-sonnet-5-5` | 1M | Text + Vision | Tool calling, structured output |
| `claude-fable-5.2` | 1M | Text + Vision | Tool calling, structured output |
| `gpt-6.1-sol` | 1M | Text + Vision | Tool calling, structured output |
| `gemini-4-argon` | 1M | Text + Vision | Tool calling, structured output |
| `deepseek/deepseek-v4-1-flash-1017` | 1M | Text + Vision | Tool calling, structured output |
| `grok-4.7` | 512K | Text + Vision | Tool calling, structured output |
| `qwen/qwen3.8-flash` | 1M | Text + Vision | Tool calling, structured output |
| `moonshotai/kimi-k3` | 1M | Text + Vision | Tool calling, structured output |
| `z-ai/glm-5.3` | 1M | Text | Tool calling, structured output |

The full model list is at [straitly.ai/models](https://straitly.ai/models).

## Configuration

1. Create an API key by following [straitly.ai/docs/quickstart](https://straitly.ai/docs/quickstart).
2. In Dify, go to **Settings -> Model Provider -> Straitly**.
3. Enter your API key. The API Base URL is optional and defaults to `https://api.straitly.ai/v1`.

Saving the key checks it against `GET /v1/key`, so an invalid key is rejected right away. Adding a model also checks that its ID is in `GET /v1/models`.

## Usage

1. After saving your API key, pick a Straitly model in a **Chatflow**, **Workflow** or **Agent** LLM node.
2. Adjust temperature, max tokens and response format (text, JSON object or JSON schema) from the model configuration panel. Tool calling works in Agent apps and Agent nodes.
3. Vision-capable models accept images from Dify's file input.

## Requirements

- A Straitly API key with prepaid credits.
- Outbound HTTPS access from the Dify plugin daemon to `api.straitly.ai`.

## Source Repository & Support

- Source repository: https://github.com/Straitly-ai/straitly-dify-plugin
- Documentation: https://straitly.ai/docs/quickstart
- Contact: support@straitly.ai
