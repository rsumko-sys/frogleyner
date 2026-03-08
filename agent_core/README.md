# agent_core — Агент приватності для HR-онбордингу та аудиту

Керований аудит персональних даних: інвентаризація профілів, аналіз приватності, план змін, виконання (API/UI/manual), DSAR-запити, аудит-лог.

## Швидкий старт

1. Скопіюйте конфіг і налаштуйте під себе:
   ```bash
   cp agent_core/config.example.yaml agent_core/config.yaml
   ```

2. Запуск з кореня репо (або `python -m agent_core.cli` з `PYTHONPATH=.`):
   ```bash
   python -m agent_core.cli --config agent_core/config.yaml inventory
   python -m agent_core.cli --config agent_core/config.yaml privacy-plan
   python -m agent_core.cli --config agent_core/config.yaml execute-plan
   python -m agent_core.cli --config agent_core/config.yaml dsar-cycle
   ```

## Команди

| Команда | Опис |
|--------|------|
| `inventory` | Зібрати інвентар профілів з усіх увімкнених платформ |
| `privacy-plan` | Побудувати план змін приватності (dry-run) |
| `execute-plan` | Виконати план (з підтвердженням у HIL-режимі) |
| `dsar-cycle` | Запустити цикл DSAR: запити на доступ/видалення, дедлайни |

## Структура

- **domain.py** — типи: ExecutionMode, HrMode, DataAsset, PlannedAction, DsarRequest тощо.
- **config.py** — завантаження YAML → AgentConfig, JurisdictionProfile, PlatformConfig.
- **connectors/** — інтерфейс PlatformConnector, StubConnector; далі — Facebook, LinkedIn, Google, Email, OSINT.
- **policy.py** — PolicyEngine (baseline vs actual → рекомендації), Planner (рекомендації → план з risk/mode).
- **execution.py** — ActionExecutor (dry-run / confirm / API / manual).
- **dsar.py** — DsarService (генерація, відправка, трекінг GDPR/UA/CCPA).
- **audit.py** — AuditLogger, AuditStore (без логування токенів/PII).
- **orchestrator.py** — Orchestrator.from_config(), run_inventory(), run_privacy_analysis(), execute_plan(), run_dsar_cycle().
- **cli.py** — CLI-обгортка.

## Режими та конфіг

- **execution_mode**: `dry_run` | `human_in_the_loop` | `auto`
- **hr_mode**: `none` | `summary_package` | `full_audit_package`
- **platforms**: увімкнення, automation_level, known_accounts, scopes
- **privacy_baseline**: general + platform_overrides для порівняння
- **jurisdiction_profile**: primary_law, applies_gdpr, ccpa_applicable, deadlines

Конектори за замовчуванням — Stub; для реальних платформ потрібні реалізації (OAuth, API, UI-автоматизація в межах ToS).
