import pytest
from pydantic import BaseModel, ConfigDict, Field


class SellerInfoResponseStructure(BaseModel):
    name: str
    sid: str
    trademark: str = Field(..., alias="tradeMark")
    model_config = ConfigDict(extra="forbid")


@pytest.fixture
def seller_info_result(wb_client):
    return wb_client.get_seller_info()  # coroutine, не await


@pytest.mark.asyncio
async def test_get_seller_info_structure(seller_info_result):
    result = await seller_info_result  # await здесь!
    SellerInfoResponseStructure.model_validate(result)


@pytest.mark.asyncio
async def test_get_seller_info_content(seller_info_result, load_testdata):
    result = await seller_info_result  # await здесь!
    expected = load_testdata["wb"]["expected_seller_info"]
    assert result == expected, f"Actual: {result}, Expected: {expected}"
