from typing import Any
from .client import StakingClient
from .types import StakeRecord, StakeRecordWithParents

def get_hotkey_stakes(
    url: str, requests: list[dict[str, Any]]
) -> list[dict[str, Any]]: ...
def get_all_hotkeys(url: str, netuid: int) -> list[str]: ...
def get_all_hotkeys_stakes_for_netuid(
    url: str, netuid: int, block_hash: str | None = None
) -> list[dict[str, Any]]: ...

__version__: str

__all__ = [
    "StakingClient",
    "StakeRecord",
    "StakeRecordWithParents",
    "__version__",
]
