import pytest
from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Warehouse(StrictModel):
    warehouse_id: int
    type: str
    name: str


class LogisticCluster(StrictModel):
    warehouses: list[Warehouse]


class Cluster(StrictModel):
    logistic_clusters: list[LogisticCluster]
    id: int
    name: str
    type: str


class OzClusterListResponseStructure(StrictModel):
    clusters: list[Cluster]


@pytest.mark.asyncio
async def test_oz_cluster_list_structure(oz_client):
    result = await oz_client.get_oz_cluster_list()
    OzClusterListResponseStructure.model_validate(result)
