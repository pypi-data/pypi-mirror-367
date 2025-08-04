import pytest
from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class CommissionList(StrictModel):
    kgvp_booking: float  = Field(..., alias="kgvpBooking")
    kgvp_marketplace: float  = Field(..., alias="kgvpMarketplace")
    kgvp_pickup: float  = Field(..., alias="kgvpPickup")
    kgvp_supplier: float  = Field(..., alias="kgvpSupplier")
    kgvp_supplier_express: float  = Field(..., alias="kgvpSupplierExpress")
    paid_storage_kgvp: float  = Field(..., alias="paidStorageKgvp")
    parent_id: int  = Field(..., alias="parentID")
    parent_name: str  = Field(..., alias="parentName")
    subject_id: int  = Field(..., alias="subjectID")
    subject_name: str  = Field(..., alias="subjectName")

class WbTariffsCommissionResponseStructure(StrictModel):
    report: list[CommissionList]


@pytest.mark.asyncio
async def test_get_seller_info_structure(wb_client):
    result = await wb_client.get_tariffs_commission()
    WbTariffsCommissionResponseStructure.model_validate(result)


