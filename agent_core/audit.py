"""Аудит-лог і докази без витоку секретів/PII."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time
import uuid

from .domain import DataAsset, PlannedAction, DsarRequest


@dataclass
class AuditEvent:
    id: str
    timestamp: float
    category: str
    actor: str
    platform: Optional[str]
    object_id: Optional[str]
    metadata: Dict[str, Any]


class AuditStore(ABC):
    """Сховище подій (append-only). Реалізації: SQLite, JSONL, S3 WORM."""

    @abstractmethod
    def append(self, event: AuditEvent) -> None:
        ...


class InMemoryAuditStore(AuditStore):
    """In-memory реалізація для тестів і CLI."""

    def __init__(self) -> None:
        self.events: List[AuditEvent] = []

    def append(self, event: AuditEvent) -> None:
        self.events.append(event)


class AuditLogger:
    """Логування подій з санітизацією (без токенів/PII)."""

    def __init__(self, store: AuditStore) -> None:
        self.store = store

    def _event(
        self,
        category: str,
        platform: Optional[str],
        object_id: Optional[str],
        metadata: Dict[str, Any],
    ) -> AuditEvent:
        safe_metadata = self._sanitize(metadata)
        return AuditEvent(
            id=str(uuid.uuid4()),
            timestamp=time.time(),
            category=category,
            actor="agent",
            platform=platform,
            object_id=object_id,
            metadata=safe_metadata,
        )

    def _sanitize(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        keys_to_mask = {"access_token", "refresh_token", "password", "email", "phone"}
        sanitized: Dict[str, Any] = {}
        for k, v in metadata.items():
            if k in keys_to_mask and isinstance(v, str):
                sanitized[k] = "***"
            else:
                sanitized[k] = v
        return sanitized

    def append(self, event: AuditEvent) -> None:
        self.store.append(event)

    def log_inventory_snapshot(self, assets: List[DataAsset]) -> None:
        event = self._event(
            category="inventory_snapshot",
            platform=None,
            object_id=None,
            metadata={"count": len(assets)},
        )
        self.append(event)

    def log_plan(self, plan: List[PlannedAction]) -> None:
        event = self._event(
            category="plan_created",
            platform=None,
            object_id=None,
            metadata={"count": len(plan)},
        )
        self.append(event)

    def log_dry_run(self, action: PlannedAction) -> None:
        event = self._event(
            category="action_dry_run",
            platform=action.platform,
            object_id=action.asset_id,
            metadata={"risk_level": action.risk_level.value},
        )
        self.append(event)

    def log_execution_result(
        self,
        action: PlannedAction,
        success: bool,
        proof: Dict[str, Any],
    ) -> None:
        event = self._event(
            category="action_executed",
            platform=action.platform,
            object_id=action.asset_id,
            metadata={"success": success},
        )
        self.append(event)

    def log_skipped(self, action: PlannedAction) -> None:
        event = self._event(
            category="action_skipped",
            platform=action.platform,
            object_id=action.asset_id,
            metadata={"reason": "confirmation_denied"},
        )
        self.append(event)

    def log_manual_required(self, action: PlannedAction) -> None:
        event = self._event(
            category="action_manual_required",
            platform=action.platform,
            object_id=action.asset_id,
            metadata={"risk_level": action.risk_level.value},
        )
        self.append(event)

    def log_dsar_sent(self, request: DsarRequest) -> None:
        event = self._event(
            category="dsar_sent",
            platform=None,
            object_id=None,
            metadata={
                "controller": request.controller_name,
                "request_type": request.request_type.value,
            },
        )
        self.append(event)
