# Obiguard Python SDK

## Security Control Panel for AI Apps

```bash
pip install obiguard
```

## Features

The Obiguard SDK is built on top of the OpenAI SDK, allowing you to seamlessly integrate Obiguard's advanced features while retaining full compatibility with OpenAI methods. With Obiguard, you can enhance your interactions with OpenAI or any other OpenAI-like provider by leveraging robust monitoring, reliability, prompt management, and more features - without modifying much of your existing code.

### Obiguard AI Gateway
<table>
    <tr>
        <td width=50%><b>Unified API Signature</b><br />If you've used OpenAI, you already know how to use Obiguard with any other provider.</td>
        <td><b>Interoperability</b><br />Write once, run with any provider. Switch between any model from_any provider seamlessly. </td>
    </tr>
    <tr>
        <td width=50%><b>Automated Fallbacks & Retries</b><br />Ensure your application remains functional even if a primary service fails.</td>
        <td><b>Load Balancing</b><br />Efficiently distribute incoming requests among multiple models.</td>
    </tr>
    <tr>
        <td width=50%><b>Semantic Caching</b><br />Reduce costs and latency by intelligently caching results.</td>
        <td><b>Virtual Keys</b><br />Secure your LLM API keys by storing them in Obiguard vault and using disposable virtual keys.</td>
    </tr>
</table>

### Observability
<table width=100%>
    <tr>
        <td width=50%><b>Logging</b><br />Keep track of all requests for monitoring and debugging.</td>
        <td width=50%><b>Requests Tracing</b><br />Understand the journey of each request for optimization.</td>
    </tr>
    <tr>
        <td width=50%><b>Custom Metadata</b><br />Segment and categorize requests for better insights.</td><td width=50%><b>Feedbacks</b><br />Coming soon - Collect and analyse weighted feedback on requests from users.</td>
    </tr>
    <tr>
        <td width=50%><b>Analytics</b><br />Track your app & LLM's performance with 40+ production-critical metrics in a single place.</td>
    </tr>
</table> 

## Usage

#### Prerequisites
1. [Sign up on Obiguard](https://obiguard.ai/) and grab your Obiguard API Key
2. Add your [OpenAI key](https://platform.openai.com/api-keys) to Obiguard's Virtual Keys page and keep it handy

```bash
# Installing the SDK
$ pip install obiguard
$ export OBIGUARD_API_KEY=<OBIGUARD API OR VIRTUAL KEY>
```

#### Making a Request to OpenAI
* Obiguard fully adheres to the OpenAI SDK signature. You can instantly switch to Obiguard and start using our production features right out of the box. <br />
* Just replace `from openai import OpenAI` with `from obiguard_ai import Obiguard`:

```py
from obiguard import Obiguard

obiguard = Obiguard(
    obiguard_api_key="OBIGUARD API OR VIRTUAL KEY"
)

chat_completion = obiguard.chat.completions.create(
    messages=[{"role": 'user', "content": 'Say this is a test'}],
    model='gpt-4'
)

print(chat_completion)
```

#### Async Usage
* Use `AsyncObiguard` instead of `Obiguard` with `await`:

```py
import asyncio
from obiguard import AsyncObiguard

obiguard = AsyncObiguard(
    obiguard_api_key="OBIGUARD API OR VIRTUAL KEY",
)


async def main():
    chat_completion = await obiguard.chat.completions.create(
        messages=[{'role': 'user', 'content': 'Say this is a test'}],
        model='gpt-4'
    )

    print(chat_completion)


asyncio.run(main())
```

## Compatibility with OpenAI SDK

Obiguard currently supports all the OpenAI methods, including the legacy ones.

| Methods                                                                                                           | OpenAI<br>V1.26.0 | Obiguard<br>V1.0.0 |
|:------------------------------------------------------------------------------------------------------------------|:--------|:-------------------|
| [Audio](https://obiguard.ai/docs/product/ai-gateway-streamline-llm-integrations/multimodal-capabilities/vision-1) | ✅ | ✅                  |
| [Chat](https://obiguard.ai/docs/api-reference/chat-completions)                                                   | ✅ | ✅                  |
| [Embeddings](https://obiguard.ai/docs/api-reference/embeddings)                                                   | ✅ | ✅                  |
| [Images](https://obiguard.ai/docs/api-reference/completions-1)                                                    | ✅ | ✅                  |
| Fine-tuning                                                                                                       | ✅     | ✅                  |
| Batch                                                                                                             | ✅     | ✅                  |
| Files                                                                                                             | ✅     | ✅                  |
| Models                                                                                                            | ✅     | ✅                  |
| Moderations                                                                                                       | ✅     | ✅                  |
| Assistants                                                                                                        | ✅     | ✅                  |
| Threads                                                                                                           | ✅     | ✅                  |
| Thread - Messages                                                                                                 | ✅     | ✅                  |
| Thread - Runs                                                                                                     | ✅     | ✅                  |
| Thread - Run - Steps                                                                                              | ✅     | ✅                  |
| Vector Store                                                                                                      | ✅     | ✅                  |
| Vector Store - Files                                                                                              | ✅     | ✅                  |
| Vector Store - Files Batches                                                                                      | ✅     | ✅                  |
| Generations                                                                                                       | ❌ (Deprecated) | ✅                  |
| Completions                                                                                                       | ❌ (Deprecated) | ✅                  |

### Obiguard-Specific Methods (Coming Soon)
| Methods                                                     | Obiguard<br>1.0.X |
|:------------------------------------------------------------|:------------------|
| [Feedback](https://obiguard.ai/docs/api-reference/feedback) | Obiguard          |
| [Prompts](https://obiguard.ai/docs/api-reference/prompts)   | Obiguard          |

---

#### [Check out Obiguard docs for the full list of supported providers](https://docs.obiguard.ai/welcome/what-is-obiguard#ai-providers-supported)

#### Contributing
Get started by checking out Github issues. Email us at support@obiguard.com.
