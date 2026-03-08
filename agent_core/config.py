"""Парсер конфігурації агента з YAML → доменні типи."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from .domain import (
    AutomationLevel,
    ExecutionMode,
    HrMode,
    JurisdictionProfile,
    PlatformConfig,
)

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def load_config(path: str | Path) -> "AgentConfig":
    """Завантажити конфіг з YAML-файлу."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    if yaml is None:
        raise RuntimeError("PyYAML required for config: pip install pyyaml")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return parse_config(raw)


def parse_config(raw: Dict[str, Any]) -> "AgentConfig":
    """Парсинг словника конфігу в AgentConfig."""
    jurisdiction = _parse_jurisdiction(raw.get("jurisdiction_profile", {}))
    platforms = _parse_platforms(raw.get("platforms", {}))
    execution = ExecutionMode(raw.get("execution_mode", "human_in_the_loop"))
    hr_mode = HrMode(raw.get("hr_mode", "summary_package"))
    privacy_baseline = raw.get("privacy_baseline", {})
    risk_thresholds = raw.get("risk_thresholds", {})
    osint = raw.get("osint", {})
    return AgentConfig(
        jurisdiction_profile=jurisdiction,
        execution_mode=execution,
        hr_mode=hr_mode,
        platforms=platforms,
        privacy_baseline=privacy_baseline,
        risk_thresholds=risk_thresholds,
        osint=osint,
        raw=raw,
    )


def _parse_jurisdiction(d: Dict[str, Any]) -> JurisdictionProfile:
    return JurisdictionProfile(
        id=d.get("id", "default"),
        primary_law=d.get("primary_law", "UA"),
        applies_gdpr=bool(d.get("applies_gdpr", True)),
        ccpa_applicable=bool(d.get("ccpa_applicable", False)),
        deadlines=d.get("deadlines", {}),
    )


def _parse_platforms(platforms_dict: Dict[str, Any]) -> Dict[str, PlatformConfig]:
    result: Dict[str, PlatformConfig] = {}
    for name, cfg in platforms_dict.items():
        if not isinstance(cfg, dict):
            continue
        result[name] = PlatformConfig(
            name=name,
            enabled=bool(cfg.get("enabled", True)),
            automation_level=AutomationLevel(
                cfg.get("automation_level", "manual_only")
            ),
            known_accounts=cfg.get("known_accounts", []),
            scopes=cfg.get("scopes", {}),
            raw=cfg,
        )
    return result


@dataclass
class AgentConfig:
    """Повний конфіг агента (не в domain.py, щоб уникнути циклів імпорту)."""

    jurisdiction_profile: JurisdictionProfile
    execution_mode: ExecutionMode
    hr_mode: HrMode
    platforms: Dict[str, PlatformConfig]
    privacy_baseline: Dict[str, Any]
    risk_thresholds: Dict[str, Any]
    osint: Dict[str, Any]
    raw: Dict[str, Any]


