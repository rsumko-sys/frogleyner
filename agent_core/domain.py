"""Доменні типи агента приватності: переліки, конфіги, сутності."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ExecutionMode(str, Enum):
    DRY_RUN = "dry_run"
    HUMAN_IN_THE_LOOP = "human_in_the_loop"
    AUTO = "auto"


class HrMode(str, Enum):
    NONE = "none"
    SUMMARY_PACKAGE = "summary_package"
    FULL_AUDIT_PACKAGE = "full_audit_package"


class AutomationLevel(str, Enum):
    API_ONLY = "api_only"
    API_PLUS_SAFE_UI = "api_plus_safe_ui"
    MANUAL_ONLY = "manual_only"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ActionKind(str, Enum):
    API = "api"
    UI = "ui"
    MANUAL = "manual"


class AssetType(str, Enum):
    PROFILE = "profile"
    POST = "post"
    CONTACT = "contact"
    EMAIL = "email"
    HR_RECORD = "hr_record"
    PROFILING_RECORD = "profiling_record"


class DsarType(str, Enum):
    ACCESS = "access"
    ERASURE = "erasure"
    PROFILING_INFO = "profiling_info"


@dataclass
class PlatformConfig:
    name: str
    enabled: bool
    automation_level: AutomationLevel
    known_accounts: List[Dict[str, Any]]
    scopes: Dict[str, bool]
    raw: Dict[str, Any]


@dataclass
class JurisdictionProfile:
    id: str
    primary_law: str
    applies_gdpr: bool
    ccpa_applicable: bool
    deadlines: Dict[str, int]


@dataclass
class DataAsset:
    platform: str
    asset_type: AssetType
    asset_id: str
    canonical_url: Optional[str]
    attributes: Dict[str, Any]
    source: str
    collected_at: float


@dataclass
class PrivacyState:
    platform: str
    asset_id: str
    settings: Dict[str, Any]


@dataclass
class PrivacyRecommendation:
    asset: DataAsset
    desired_state: Dict[str, Any]
    current_state: PrivacyState
    risk_level: RiskLevel


@dataclass
class PlannedAction:
    platform: str
    asset_id: str
    description: str
    action_kind: ActionKind
    risk_level: RiskLevel
    payload: Dict[str, Any]
    requires_confirmation: bool


@dataclass
class DsarRequest:
    controller_name: str
    controller_contact: str
    request_type: DsarType
    jurisdiction: JurisdictionProfile
    subject_identifiers: Dict[str, Any]
    requested_at: float
