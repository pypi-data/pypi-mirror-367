import httpx
import asyncio
import signal
import sys
from datetime import datetime
from colorama import Fore, Style, init
from httpx import HTTPStatusError, RequestError

init(autoreset=True)

class TrennyClient:
    def __init__(self, *, apikey: str, auto_ping: bool = True):
        if not apikey:
            raise ValueError("Missing API key")
        
        self.base_url = "https://0g7mt1j6-3000.euw.devtunnels.ms".rstrip('/')
        self.apikey = apikey
        self.auto_ping = auto_ping
        self.client = httpx.AsyncClient()
        self.headers = {"x-api-key": self.apikey}

        if auto_ping:
            asyncio.create_task(self.ping("started"))
            loop = asyncio.get_event_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self._exit_handler()))

    async def _exit_handler(self):
        await self.ping("stopped")
        await self.client.aclose()
        print(f"{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
        sys.exit(0)

    async def ping(self, status: str):
        try:
            await self.client.post(
                f"{self.base_url}/api/logs",
                headers=self.headers,
                json={
                    "status": status,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            print(f"{Fore.GREEN}[TrennyClient] Sent '{status}' ping.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[TrennyClient] Failed to ping '{status}': {e}{Style.RESET_ALL}")

    async def verify(self, endpoint: str = "default") -> bool:
        try:
            resp = await self.client.get(f"{self.base_url}/api/verify", params={
                "key": self.apikey,
                "endpoint": endpoint
            })
            resp.raise_for_status()
            data = resp.json()
            if data.get("valid"):
                return True
            raise ValueError(f"{Fore.RED}API key invalid or revoked{Style.RESET_ALL}")
        except HTTPStatusError as e:
            msg = e.response.text
            raise ValueError(f"{Fore.RED}API verify failed: {msg}{Style.RESET_ALL}")
        except RequestError as e:
            raise ValueError(f"{Fore.RED}Network error: {str(e)}{Style.RESET_ALL}")
        except Exception as e:
            raise ValueError(f"{Fore.RED}Unexpected verify error: {str(e)}{Style.RESET_ALL}")
        
    async def get_stats(self):
        try:
            resp = await self.client.get(f"{self.base_url}/api/stats", headers=self.headers)
            resp.raise_for_status()
            return resp.json()
        except HTTPStatusError as e:
            msg = e.response.text
            raise ValueError(f"{Fore.RED}Failed to get stats: {msg}{Style.RESET_ALL}")
        except RequestError as e:
            raise ValueError(f"{Fore.RED}Network error while getting stats: {str(e)}{Style.RESET_ALL}")
        except Exception as e:
            raise ValueError(f"{Fore.RED}Unexpected stats error: {str(e)}{Style.RESET_ALL}")

    async def get_logs(self):
        try:
            resp = await self.client.get(f"{self.base_url}/api/logs", headers=self.headers)
            resp.raise_for_status()
            return resp.json()
        except HTTPStatusError as e:
            msg = e.response.text
            raise ValueError(f"{Fore.RED}Failed to get logs: {msg}{Style.RESET_ALL}")
        except RequestError as e:
            raise ValueError(f"{Fore.RED}Network error while getting logs: {str(e)}{Style.RESET_ALL}")
        except Exception as e:
            raise ValueError(f"{Fore.RED}Unexpected logs error: {str(e)}{Style.RESET_ALL}")

    async def revoke_key(self):
        try:
            resp = await self.client.post(
                f"{self.base_url}/api/revoke",
                headers=self.headers,
                json={}
            )
            resp.raise_for_status()
            return resp.json()
        except HTTPStatusError as e:
            msg = e.response.text
            raise ValueError(f"{Fore.RED}Failed to revoke key: {msg}{Style.RESET_ALL}")
        except RequestError as e:
            raise ValueError(f"{Fore.RED}Network error while revoking key: {str(e)}{Style.RESET_ALL}")
        except Exception as e:
            raise ValueError(f"{Fore.RED}Unexpected revoke error: {str(e)}{Style.RESET_ALL}")

    async def close(self):
        await self.client.aclose()
