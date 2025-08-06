# python-ai-tracer

`python-ai-tracer` is a Python instrumentation library for tracing AI/LLM calls and exporting spans to a Watchlog agent. It supports batching, persistence, and automatic environment detection (local vs. Kubernetes).

## Features

- **Lightweight tracer**: start and end spans to capture timing, cost, tokens, model, provider, input/output.
- **Batching & persistence**: automatically buffers spans on disk and flushes in the background or on-demand.
- **Kubernetes-friendly**: auto-detects K8s environment to select the correct agent URL.
- **Configurable**: customize batch size, flush intervals, retry behavior, sensitive field redaction, and more.

## Installation

```bash
pip install python-ai-tracer
```

## Usage

```python
from watchlog_ai_tracer import WatchlogTracer
import time

# Initialize tracer with your app name
tracer = WatchlogTracer(app="myapp")

# Start a new trace
tracer.start_trace()

# Root span
root_id = tracer.start_span("handle_request", metadata={"feature": "ai-summary"})

# Child span: validation
val_id = tracer.child_span(root_id, "validate_input")
# end validation span
tracer.end_span(val_id, {
    "tokens": 0,
    "cost": 0,
    "model": "",
    "provider": "",
    "input": "",
    "output": ""
})

# Child span: LLM call
llm_id = tracer.child_span(root_id, "call_llm")
# simulate work
time.sleep(0.5)
tracer.end_span(llm_id, {
    "tokens": 42,
    "cost": 0.002,
    "model": "gpt-4",
    "provider": "openai",
    "input": "Summarize: Hello world...",
    "output": "Hello world summary."
})

# End root span
tracer.end_span(root_id, {})

# Flush all spans to agent immediately
tracer.send()
```

## API

### `WatchlogTracer(config)`

- `app` (str, required): your application name.
- `agent_url` (str, optional): override the default agent endpoint.
- `batch_size` (int): number of spans per HTTP batch.
- `flush_on_span_count` (int): completed spans to auto-enqueue.
- `auto_flush_interval` (int): ms between background flushes.
- `max_retries` (int): HTTP retry attempts.
- `max_queue_size` (int): max spans to keep on disk.
- `queue_item_ttl` (int): TTL (ms) for queued spans.
- ... (see docstrings in `__init__`).

### Methods

- `start_trace() -> trace_id`: begins a new trace.
- `start_span(name, metadata={}) -> span_id`: starts a new span.
- `child_span(parent_id, name, metadata={}) -> span_id`: shorthand for nested span.
- `end_span(span_id, data={})`: ends a span, records metrics.
- `send()`: ends any open spans, enqueues, and immediately flushes all spans to the agent.
- `flush_queue()`: manually trigger a background queue flush (async).

## Configuration & Environment

- **Local**: defaults to `http://127.0.0.1:3774/ai-tracer`.
- **Kubernetes**: if running in K8s (service account & DNS check), auto-switches to `http://watchlog-node-agent.monitoring.svc.cluster.local:3774/ai-tracer`.
- Override via `agent_url` parameter.

## Contributing

PRs welcome! Please file issues on [GitHub](https://github.com/Watchlog-monitoring/python-ai-tracer).

---

*Documentation generated from version 1.0.0.*