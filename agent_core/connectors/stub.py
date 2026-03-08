"""Заглушка-конектор для тестів і платформ без реалізації."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple

from ..domain import DataAsset, PlannedAction, PrivacyState, AssetType
from ..domain import PlatformConfig
from .base import PlatformConnector
import time


class StubConnector(PlatformConnector):
    """Конектор, що нічого не робить; повертає порожні результати."""

    def discover_accounts(self) -> Iterable[DataAsset]:
        for acc in self.config.known_accounts:
            url = acc.get("profile_url") or acc.get("email", "")
            yield DataAsset(
                platform=self.config.name,
                asset_type=AssetType.PROFILE,
                asset_id=url or "stub",
                canonical_url=url,
                attributes=acc,
                source="config",
                collected_at=time.time(),
            )

    def collect_inventory(self, seeds: Iterable[DataAsset]) -> Iterable[DataAsset]:
        yield from seeds

    def read_privacy_state(self, assets: Iterable[DataAsset]) -> Iterable[PrivacyState]:
        for a in assets:
            yield PrivacyState(
                platform=a.platform,
                asset_id=a.asset_id,
                settings={"stub": True},
            )

    def apply_action(self, action: PlannedAction) -> Tuple[bool, Dict[str, Any]]:
        return True, {"stub": True}

    def delete_object(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        return False, {"reason": "stub_no_delete"}
