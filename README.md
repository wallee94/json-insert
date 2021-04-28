![Build Status](https://github.com/wallee94/json-insert/actions/workflows/tests.yaml/badge.svg)

# JSON Insert

JSON Insert allows adding new keys to a json stream without storing it in memory.

## Installation

Install it in your environment

```shell
pip install json-insert
```

## Usage

A common usage is in the context of forwarding a response to a streaming web endpoint.

This is an example that inserts a "timestamp" key to a forwarded json, using Starlette
and the async method `astream`

```python
import httpx
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse

client = httpx.AsyncClient()

async def home(request):
    req = client.build_request("GET", "https://www.example.com/")
    r = await client.send(req, stream=True)

    insert = {
        'timestamp': datetime.utcnow().isoformat()
    }
    streamer = json_insert.JSONStream(insert)
    return StreamingResponse(
        streamer.astream(r.aiter_text()), background=BackgroundTask(r.aclose))
```

The same can be done using `requests`

```python
def iter_content(url):
    insert = {
        'timestamp': datetime.utcnow().isoformat()
    }
    streamer = json_insert.JSONStream(insert)
    with requests.get(url, stream=True) as r:
        yield from streamer.stream(r.iter_content(decode_unicode=True))
```