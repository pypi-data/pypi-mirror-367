# TrennyClient

**Asynchronous Python client for interacting with the Trenny API.**

---

## Features

- API key verification  
- Fetch service statistics  
- Retrieve logs  
- Automatic startup and shutdown pings  
- Revoke API keys  
- Async and efficient with `httpx` and `asyncio`  
- Color-coded console output for easy debugging  

---

## Installation

```bash
pip install httpx colorama
```

## Usage Example

```python
import asyncio
from trenny_client import TrennyClient

async def main():
    client = TrennyClient(apikey="YOUR_API_KEY")

    is_valid = await client.verify()
    print(f"API key valid: {is_valid}")

    stats = await client.get_stats()
    print("Stats:", stats)

    logs = await client.get_logs()
    print("Logs:", logs)

    await client.close()

asyncio.run(main())
```

## API Overview

```py
TrennyClient(apikey: str, auto_ping: bool = True): # Initialize the client.

async ping(status: str): # Send a manual ping.

async verify(endpoint: str = "default") -> bool: # Verify your API key.

async get_stats() -> dict: # Get service stats.

async get_logs() -> dict: # Retrieve logs.

async revoke_key() -> dict: # Revoke your API key.

async close(): # Close the HTTP client session.
```

### Notes

**Uses asynchronous programming (asyncio, httpx).**

**Sends API key in the x-api-key HTTP header.**

**Automatically sends "started" and "stopped" pings by default.**

**Exceptions raised on network or authorization errors — use try/except.**
