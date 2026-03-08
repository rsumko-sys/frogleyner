"""CLI агента: inventory, privacy-plan, execute-plan, dsar-cycle."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config
from .orchestrator import Orchestrator


def _config_path() -> Path:
    return Path("config.yaml")


def cmd_inventory(args: argparse.Namespace) -> int:
    """Зібрати інвентар профілів."""
    config = load_config(args.config)
    orch = Orchestrator.from_config(config)
    assets = orch.run_inventory()
    print(f"Inventory: {len(assets)} assets")
    for a in assets:
        print(f"  - {a.platform} | {a.asset_type.value} | {a.asset_id}")
    return 0


def cmd_privacy_plan(args: argparse.Namespace) -> int:
    """Побудувати план змін приватності (без виконання)."""
    config = load_config(args.config)
    orch = Orchestrator.from_config(config)
    assets = orch.run_inventory()
    plan = orch.run_privacy_analysis(assets)
    print(f"Plan: {len(plan)} actions")
    for p in plan:
        print(f"  - {p.platform} | {p.asset_id} | {p.action_kind.value} | risk={p.risk_level.value}")
    return 0


def cmd_execute_plan(args: argparse.Namespace) -> int:
    """Виконати план (з підтвердженням у HIL-режимі)."""
    config = load_config(args.config)
    orch = Orchestrator.from_config(config)
    assets = orch.run_inventory()
    plan = orch.run_privacy_analysis(assets)
    orch.execute_plan(plan)
    print("Execute plan done. Check audit log.")
    return 0


def cmd_dsar_cycle(args: argparse.Namespace) -> int:
    """Запустити цикл DSAR: створення/відправка запитів, перевірка дедлайнів."""
    config = load_config(args.config)
    orch = Orchestrator.from_config(config)
    orch.run_dsar_cycle()
    print("DSAR cycle done.")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Повний цикл: інвентаризація → план → виконання → DSAR."""
    config = load_config(args.config)
    orch = Orchestrator.from_config(config)
    assets = orch.run_inventory()
    print(f"Inventory: {len(assets)} assets")
    plan = orch.run_privacy_analysis(assets)
    print(f"Plan: {len(plan)} actions")
    orch.execute_plan(plan)
    print("Execute plan done.")
    orch.run_dsar_cycle()
    print("DSAR cycle done.")
    print("Run complete. Check audit log for details.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Privacy Agent CLI")
    parser.add_argument(
        "--config",
        type=Path,
        default=_config_path(),
        help="Path to config.yaml",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("inventory", help="Collect profile inventory")
    sub.add_parser("privacy-plan", help="Build privacy change plan (no execution)")
    sub.add_parser("execute-plan", help="Execute privacy plan")
    sub.add_parser("dsar-cycle", help="Run DSAR request cycle")
    sub.add_parser("run", help="Run full cycle: inventory, plan, execute, dsar")
    args = parser.parse_args()
    handlers = {
        "inventory": cmd_inventory,
        "privacy-plan": cmd_privacy_plan,
        "execute-plan": cmd_execute_plan,
        "dsar-cycle": cmd_dsar_cycle,
        "run": cmd_run,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
