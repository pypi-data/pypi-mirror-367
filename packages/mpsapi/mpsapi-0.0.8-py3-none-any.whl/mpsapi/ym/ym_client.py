from typing import Literal

import aiohttp


class YMClient:
    def __init__(self, campaign_id: int, business_id: int, api_key: str, session: aiohttp.ClientSession | None = None):
        self.api_key = api_key
        self.campaign_id = campaign_id
        self.business_id = business_id
        self.session = session or aiohttp.ClientSession(
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
        )

    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def get_warehouses(self):
        """Возвращает список складов Маркета с их идентификаторами
        https://yandex.ru/dev/market/partner-api/doc/ru/reference/warehouses/getFulfillmentWarehouses"""
        url = "https://api.partner.market.yandex.ru/warehouses?"
        # params = {}
        # async with self.session.get(url, params=params) as resp:
        async with self.session.get(url) as resp:
            return await resp.json()
