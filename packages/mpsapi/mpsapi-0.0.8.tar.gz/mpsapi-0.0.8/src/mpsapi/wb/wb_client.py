from datetime import date
from typing import Literal

import aiohttp


class WBClient:
    BASE_URL = "https://common-api.wildberries.ru"

    def __init__(self, api_key: str, session: aiohttp.ClientSession | None = None):
        self.api_key = api_key
        self.session = session or aiohttp.ClientSession(headers={"Authorization": self.api_key})

    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def get_seller_info(self):
        url = f"{self.BASE_URL}/api/v1/seller-info"
        params = {}
        async with self.session.get(url, params=params) as resp:
            return await resp.json()

    async def get_news(
        self,
        *,
        from_dt: date | None = None,
        from_id: int | None = None,
    ):
        if bool(from_dt) == bool(from_id):
            raise ValueError(
                "Передайте только один из параметров: либо from_dt, либо from_id, но не оба и не ни одного."
            )
        params = {"fromID": str(from_id)} if from_id is not None else {"from": from_dt.isoformat()}

        url = f"{self.BASE_URL}/api/communications/v2/news"
        async with self.session.get(url, params=params) as resp:
            return await resp.json()

    async def get_tariffs_commission(
        self,
        *,
        locale: Literal["ru", "en", "zh"] = "ru",
    ):
        url = f"{self.BASE_URL}/api/v1/tariffs/commission"
        async with self.session.get(url, params={"locale": locale}) as resp:
            return await resp.json()
