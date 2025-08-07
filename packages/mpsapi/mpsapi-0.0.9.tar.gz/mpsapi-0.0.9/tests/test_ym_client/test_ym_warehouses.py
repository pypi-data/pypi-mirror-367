import pytest
from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GPSModel(StrictModel):
    latitude: float
    longitude: float


class AddressModel(StrictModel):
    city: str
    street: str
    number: str
    gps: GPSModel
    building: str | None = None
    block: str | None = None


class WarehouseModel(StrictModel):
    id: int
    name: str
    address: AddressModel


class ResultModel(StrictModel):
    warehouses: list[WarehouseModel]


class RootModel(StrictModel):
    status: str
    result: ResultModel


@pytest.mark.asyncio
async def test_get_ym_warehouses(ym_client):
    result = await ym_client.get_warehouses()
    assert result["status"] == "OK"
    RootModel.model_validate(result)
