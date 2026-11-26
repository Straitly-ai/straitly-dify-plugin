# Privacy

This plugin sends the configured Straitly API key and language-model requests
directly to `https://api.straitly.ai/v1` (or the custom API Base URL explicitly
configured by the user). Requests may include model IDs, prompts, conversation
messages, images (for vision-capable models), tool definitions and inference
parameters. Generated completions, usage statistics and errors are returned to
Dify.

The plugin itself collects nothing, stores nothing, writes no logs and adds no
analytics or third-party telemetry. How Straitly handles API requests is
described in the [Straitly Privacy Policy](https://straitly.ai/privacy) and
[Terms](https://straitly.ai/terms).
