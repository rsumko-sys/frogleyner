"""Політики приватності та планувальник дій."""
from __future__ import annotations

from typing import Any, Dict, List

from .domain import (
    AutomationLevel,
    ActionKind,
    DataAsset,
    ExecutionMode,
    PlannedAction,
    PrivacyRecommendation,
    PrivacyState,
    RiskLevel,
)
from .domain import PlatformConfig


class PolicyEngine:
    """Порівняння поточного стану з baseline і формування рекомендацій."""

    def __init__(self, privacy_baseline: Dict[str, Any]) -> None:
        self.privacy_baseline = privacy_baseline

    def build_recommendations(
        self,
        assets: List[DataAsset],
        states: List[PrivacyState],
    ) -> List[PrivacyRecommendation]:
        by_asset_id = {(s.platform, s.asset_id): s for s in states}
        result: List[PrivacyRecommendation] = []
        for asset in assets:
            state = by_asset_id.get((asset.platform, asset.asset_id))
            if not state:
                continue
            desired = self._desired_state_for(asset)
            risk = self._risk_for(asset, state, desired)
            result.append(
                PrivacyRecommendation(
                    asset=asset,
                    desired_state=desired,
                    current_state=state,
                    risk_level=risk,
                )
            )
        return result

    def _desired_state_for(self, asset: DataAsset) -> Dict[str, Any]:
        general = self.privacy_baseline.get("general", {})
        platform_overrides = self.privacy_baseline.get("platform_overrides", {})
        platform_specific = platform_overrides.get(asset.platform, {})
        merged = dict(general)
        merged.update(platform_specific)
        return merged

    def _risk_for(
        self,
        asset: DataAsset,
        current: PrivacyState,
        desired: Dict[str, Any],
    ) -> RiskLevel:
        # Спрощена евристика: якщо поточний стан відрізняється — medium
        if current.settings.get("stub"):
            return RiskLevel.LOW
        diff_keys = set(desired.keys()) - set(current.settings.keys())
        if diff_keys or any(
            current.settings.get(k) != desired.get(k) for k in desired
        ):
            return RiskLevel.MEDIUM
        return RiskLevel.LOW


class Planner:
    """Перетворення рекомендацій у план дій з урахуванням режиму та рівня автоматизації."""

    def __init__(self, platform_configs: Dict[str, PlatformConfig]) -> None:
        self.platform_configs = platform_configs

    def build_plan(
        self,
        recommendations: List[PrivacyRecommendation],
        mode: ExecutionMode,
    ) -> List[PlannedAction]:
        plan: List[PlannedAction] = []
        for rec in recommendations:
            platform_config = self.platform_configs.get(rec.asset.platform)
            if not platform_config or not platform_config.enabled:
                continue
            automation_level = platform_config.automation_level
            action_kind = self._select_action_kind(automation_level)
            requires_confirmation = self._requires_confirmation(rec.risk_level, mode)
            plan.append(
                PlannedAction(
                    platform=rec.asset.platform,
                    asset_id=rec.asset.asset_id,
                    description="adjust_privacy_settings",
                    action_kind=action_kind,
                    risk_level=rec.risk_level,
                    payload=rec.desired_state,
                    requires_confirmation=requires_confirmation,
                )
            )
        return plan

    def _select_action_kind(self, level: AutomationLevel) -> ActionKind:
        if level == AutomationLevel.API_ONLY:
            return ActionKind.API
        if level == AutomationLevel.API_PLUS_SAFE_UI:
            return ActionKind.API  # можна розширити на UI для safe-дій
        return ActionKind.MANUAL

    def _requires_confirmation(self, risk: RiskLevel, mode: ExecutionMode) -> bool:
        if mode == ExecutionMode.DRY_RUN:
            return True
        if mode == ExecutionMode.AUTO:
            return risk != RiskLevel.LOW
        if mode == ExecutionMode.HUMAN_IN_THE_LOOP:
            return risk == RiskLevel.HIGH
        return True
