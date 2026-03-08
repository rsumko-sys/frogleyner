"""Оркестратор: інвентаризація → аналіз приватності → план → виконання → DSAR → аудит."""
from __future__ import annotations

from typing import Dict, List, TYPE_CHECKING

from .domain import (
    DataAsset,
    ExecutionMode,
    HrMode,
    JurisdictionProfile,
    PlannedAction,
    PrivacyState,
)
from .connectors.base import PlatformConnector
from .connectors.stub import StubConnector
from .policy import PolicyEngine, Planner
from .execution import ActionExecutor
from .audit import AuditLogger, AuditStore, InMemoryAuditStore
from .dsar import DsarService

if TYPE_CHECKING:
    from .config import AgentConfig


class Orchestrator:
    """Єдина точка запуску: inventory → privacy analysis → plan → execute → dsar."""

    def __init__(
        self,
        execution_mode: ExecutionMode,
        hr_mode: HrMode,
        jurisdiction: JurisdictionProfile,
        platform_connectors: Dict[str, PlatformConnector],
        policy_engine: PolicyEngine,
        planner: Planner,
        executor: ActionExecutor,
        dsar_service: "DsarService",
        audit_logger: AuditLogger,
    ) -> None:
        from .domain import ExecutionMode, HrMode, JurisdictionProfile

        self.execution_mode = execution_mode
        self.hr_mode = hr_mode
        self.jurisdiction = jurisdiction
        self.platform_connectors = platform_connectors
        self.policy_engine = policy_engine
        self.planner = planner
        self.executor = executor
        self.dsar_service = dsar_service
        self.audit_logger = audit_logger

    @classmethod
    def from_config(
        cls,
        config: "AgentConfig",
        audit_store: AuditStore | None = None,
        connectors_overrides: Dict[str, PlatformConnector] | None = None,
    ) -> "Orchestrator":
        """Зібрати оркестратор з конфігу. Конектори — Stub, якщо не передані override."""
        store = audit_store or InMemoryAuditStore()
        audit_logger = AuditLogger(store)
        connectors: Dict[str, PlatformConnector] = {}
        for name, platform_cfg in config.platforms.items():
            if not platform_cfg.enabled:
                continue
            if connectors_overrides and name in connectors_overrides:
                connectors[name] = connectors_overrides[name]
            else:
                connectors[name] = StubConnector(platform_cfg)
        policy_engine = PolicyEngine(config.privacy_baseline)
        planner = Planner(config.platforms)
        executor = ActionExecutor(connectors, audit_logger)
        dsar_service = DsarService(audit_logger)
        return cls(
            execution_mode=config.execution_mode,
            hr_mode=config.hr_mode,
            jurisdiction=config.jurisdiction_profile,
            platform_connectors=connectors,
            policy_engine=policy_engine,
            planner=planner,
            executor=executor,
            dsar_service=dsar_service,
            audit_logger=audit_logger,
        )

    def run_inventory(self) -> List[DataAsset]:
        """Зібрати інвентар з усіх увімкнених платформ, дедуп, записати в аудит."""
        assets: List[DataAsset] = []
        for name, connector in self.platform_connectors.items():
            discovered = list(connector.discover_accounts())
            detailed = list(connector.collect_inventory(discovered))
            assets.extend(discovered)
            assets.extend(detailed)
        deduped = self._deduplicate_assets(assets)
        self.audit_logger.log_inventory_snapshot(deduped)
        return deduped

    def _deduplicate_assets(self, assets: List[DataAsset]) -> List[DataAsset]:
        by_key: Dict[tuple, DataAsset] = {}
        for asset in assets:
            key = (asset.platform, asset.asset_type, asset.asset_id or asset.canonical_url)
            if key not in by_key:
                by_key[key] = asset
        return list(by_key.values())

    def run_privacy_analysis(self, assets: List[DataAsset]) -> List[PlannedAction]:
        """Зняти стан приватності, порівняти з baseline, побудувати план."""
        privacy_states: List[PrivacyState] = []
        for name, connector in self.platform_connectors.items():
            platform_assets = [a for a in assets if a.platform == name]
            if not platform_assets:
                continue
            states = list(connector.read_privacy_state(platform_assets))
            privacy_states.extend(states)
        recommendations = self.policy_engine.build_recommendations(assets, privacy_states)
        plan = self.planner.build_plan(recommendations, self.execution_mode)
        self.audit_logger.log_plan(plan)
        return plan

    def execute_plan(self, plan: List[PlannedAction]) -> None:
        """Виконати план з урахуванням режиму та підтверджень."""
        self.executor.execute(plan, self.execution_mode)

    def run_dsar_cycle(self) -> None:
        """Створити/відправити DSAR-запити та перевірити дедлайни."""
        if self.hr_mode == HrMode.NONE:
            return
        self.dsar_service.ensure_requests_created(self.jurisdiction)
        self.dsar_service.check_deadlines()
        self.dsar_service.update_statuses()
