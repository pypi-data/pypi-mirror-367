from datetime import date

import pytest


@pytest.mark.asyncio
async def test_neither_dt_nor_last_news_id_raises(wb_client):
    with pytest.raises(ValueError, match="Передайте только один из параметров: либо from_dt, либо from_id, но не оба и не ни одного."):
        await wb_client.get_news()


@pytest.mark.asyncio
async def test_both_dt_and_last_news_id_raises(wb_client):
    with pytest.raises(ValueError, match="Передайте только один из параметров: либо from_dt, либо from_id, но не оба и не ни одного."):
        await wb_client.get_news(from_dt=date.today(), from_id=123)


@pytest.mark.asyncio
async def test_get_news_with_specific_date(wb_client):
    custom_date = date(2025, 1, 1)
    result = await wb_client.get_news(from_dt=custom_date)
    expected = {
        "content": "Стоимость приёмки за единицу товара — бесплатно весь день. Перейти к карте складов",
        "date": "2025-01-03T12:25:51+03:00",
        "header": "С 12:00 3 января на складе «Софьино» действует бесплатная приёмка товаров по модели «Маркетплейс» (FBS)",
        "id": 7179,
        "types": [{"id": 6, "name": "Маркетплейс (FBS)"}],
    }
    print(f'result test_get_news_with_specific_date: {result}')
    assert not result["additionalErrors"]
    assert len(result["data"]) == 100
    assert result["data"][0] == expected


@pytest.mark.asyncio
async def test_get_news_with_specific_news_id(wb_client):
    custom_news_id = 7179
    result = await wb_client.get_news(from_id=custom_news_id)
    expected = {
        "content": "Стоимость приёмки за единицу товара — бесплатно весь день. Перейти к карте складов",
        "date": "2025-01-03T12:25:51+03:00",
        "header": "С 12:00 3 января на складе «Софьино» действует бесплатная приёмка товаров по модели «Маркетплейс» (FBS)",
        "id": 7179,
        "types": [{"id": 6, "name": "Маркетплейс (FBS)"}],
    }
    print(f'result test_get_news_with_specific_news_id: {result}')
    assert not result["additionalErrors"]
    assert len(result["data"]) == 100
    assert result["data"][0] == expected


