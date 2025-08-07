import pytest
import pytest_asyncio
import yaml
from dotenv import dotenv_values
from loguru import logger

from mpsapi.oz.oz_client import OZClient
from mpsapi.wb.wb_client import WBClient
from mpsapi.ym.ym_client import YMClient


# @pytest.fixture(scope="module")
@pytest.fixture(scope="session")
def load_config(path: str = ".env") -> dict[str, str]:
    config = dotenv_values(path)
    required_keys = [
        "WB_API_KEY_BRUSTANCE",
        "OZ_CLIENT_ID_BRUSTANCE",
        "OZ_API_KEY_BRUSTANCE",
        "YM_API_KEY",
        "YM_CAMPAIGN_ID",
        "YM_BUSINESS_ID",
    ]
    missing = [k for k in required_keys if k not in config]
    logger.debug("Loaded config")
    if missing:
        raise RuntimeError(f"Missing required config keys: {missing}")
    return config


@pytest.fixture(scope="module")
def load_testdata() -> dict[str, dict[str, str]]:

    with open("testdata.yaml", "r") as file:
        creds = yaml.safe_load(file)
    # creds = Box(creds)

    return creds


@pytest_asyncio.fixture
async def wb_client(load_config):
    async with WBClient(api_key=load_config["WB_API_KEY_BRUSTANCE"]) as client:
        yield client


@pytest_asyncio.fixture
async def oz_client(load_config):
    async with OZClient(
        client_id=load_config["OZ_CLIENT_ID_BRUSTANCE"], api_key=load_config["OZ_API_KEY_BRUSTANCE"]
    ) as client:
        yield client


@pytest_asyncio.fixture
async def ym_client(load_config):
    async with YMClient(
        campaign_id=int(load_config["YM_CAMPAIGN_ID"]),
        business_id=int(load_config["YM_BUSINESS_ID"]),
        api_key=load_config["YM_API_KEY"],
    ) as client:
        yield client
