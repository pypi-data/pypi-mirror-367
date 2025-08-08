import unittest
import asyncio
from trenny_client.trenny_client import TrennyClient

class TestTrennyClient(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = TrennyClient(
            apikey="trenny.df08fb52c99c9521b7a0f34ee8ab241e",
            auto_ping=False
        )

    async def asyncTearDown(self):
        await self.client.close()

    async def test_ping(self):
        await self.client.ping("test")

    async def test_verify(self):
        try:
            result = await self.client.verify()
            self.assertIsInstance(result, bool)
        except Exception as e:
            self.fail(f"verify() raised exception: {e}")

    async def test_get_stats(self):
        try:
            stats = await self.client.get_stats()
            self.assertIsInstance(stats, dict)
        except Exception as e:
            self.fail(f"get_stats() raised exception: {e}")

    async def test_get_logs(self):
        try:
            logs = await self.client.get_logs()
            self.assertIsInstance(logs, list)
        except Exception as e:
            self.fail(f"get_logs() raised exception: {e}")

if __name__ == "__main__":
    unittest.main()
