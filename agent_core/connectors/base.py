"""Базовий інтерфейс конектора платформи."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Tuple

from ..domain import (
    DataAsset,
    PlannedAction,
    PrivacyState,
)
from ..domain import PlatformConfig


class PlatformConnector(ABC):
    """Абстрактний конектор: інвентаризація, стан приватності, виконання дій."""

    def __init__(self, config: PlatformConfig) -> None:
        self.config = config

    @abstractmethod
    def discover_accounts(self) -> Iterable[DataAsset]:
        """Виявити акаунти з known_accounts та OAuth (якщо є)."""
        ...

    @abstractmethod
    def collect_inventory(self, seeds: Iterable[DataAsset]) -> Iterable[DataAsset]:
        """Зібрати детальний інвентар по заданих сідах."""
        ...

    @abstractmethod
    def read_privacy_state(self, assets: Iterable[DataAsset]) -> Iterable[PrivacyState]:
        """Прочитати поточний стан приватності для активів."""
        ...

    @abstractmethod
    def apply_action(self, action: PlannedAction) -> Tuple[bool, Dict[str, Any]]:
        """Застосувати дію (налаштування приватності). Повертає (success, proof)."""
        ...

    @abstractmethod
    def delete_object(self, asset: DataAsset) -> Tuple[bool, Dict[str, Any]]:
        """Видалити об'єкт (пост/контакт/тощо), якщо дозволено API/ToS. Повертає (success, proof)."""
        ...
