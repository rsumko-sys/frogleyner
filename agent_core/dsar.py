"""Сервіс запитів на доступ/видалення (DSAR): генерація, відправка, трекінг дедлайнів."""
from __future__ import annotations

from typing import List, TYPE_CHECKING

from .domain import DsarRequest, DsarType, JurisdictionProfile

if TYPE_CHECKING:
    from .audit import AuditLogger


class DsarService:
    """Підготовка і трекінг GDPR/Україна/CCPA запитів."""

    def __init__(self, audit_logger: "AuditLogger") -> None:
        self.audit_logger = audit_logger
        self._pending: List[DsarRequest] = []

    def ensure_requests_created(self, jurisdiction: JurisdictionProfile) -> None:
        """Створити необхідні запити за юрисдикцією (за потреби)."""
        pending: List[DsarRequest] = list(self._pending)
        for req in pending:
            self._send(req)
            self.audit_logger.log_dsar_sent(req)

    def _send(self, request: DsarRequest) -> None:
        # TODO: SMTP або відправка через портал контролера
        pass

    def check_deadlines(self) -> None:
        """Перевірити дедлайни відповідей і нагадати при потребі."""
        pass

    def update_statuses(self) -> None:
        """Оновити статуси відповідей на запити."""
        pass
