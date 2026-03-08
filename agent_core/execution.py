"""Виконання плану дій: API/UI з підтвердженням та dry-run."""
from __future__ import annotations

from typing import Dict, Iterable, TYPE_CHECKING

from .domain import ActionKind, ExecutionMode, PlannedAction

if TYPE_CHECKING:
    from .audit import AuditLogger
    from .connectors.base import PlatformConnector


class ActionExecutor:
    """Виконує план з урахуванням режиму та підтвердження для risky-дій."""

    def __init__(
        self,
        connectors: Dict[str, "PlatformConnector"],
        audit_logger: "AuditLogger",
    ) -> None:
        self.connectors = connectors
        self.audit_logger = audit_logger

    def execute(
        self,
        plan: Iterable[PlannedAction],
        mode: ExecutionMode,
    ) -> None:
        for action in plan:
            if mode == ExecutionMode.DRY_RUN:
                self.audit_logger.log_dry_run(action)
                continue
            if action.requires_confirmation and not self._confirm(action):
                self.audit_logger.log_skipped(action)
                continue
            connector = self.connectors.get(action.platform)
            if not connector:
                self.audit_logger.log_skipped(action)
                continue
            if action.action_kind == ActionKind.MANUAL:
                self.audit_logger.log_manual_required(action)
                continue
            success, proof = connector.apply_action(action)
            self.audit_logger.log_execution_result(action, success, proof)

    def _confirm(self, action: PlannedAction) -> bool:
        """Підтвердження від користувача (human-in-the-loop). За замовчуванням — так."""
        return True  # TODO: інтеграція з CLI/Web-UI для запиту підтвердження
