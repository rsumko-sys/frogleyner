# Дані для аналізу (privacy agent)

Ця папка містить джерела даних про профіль для агента приватності та HR-онбордингу.

## Файли

- **cv_pack_exporter.py** — скрипт експорту CV-паку (miltech/defense-adjacent): master CV, таргетовані CV, cover letter, LinkedIn about, interview prep. Редагуйте блоки в скрипті й запускайте; результат у `output_cv_pack/`. Ідентифікатори з `PROFILE` використовуються як «дані для аналізу» агента.
- **profile_identifiers.yaml** — витяг ідентифікаторів (ім’я, email, телефон, Signal, LinkedIn, location) для конфігу агента. Можна підставляти в `known_accounts` та використовувати для OSINT allowed_identifiers.

## Зв’язок з агентом

- У `config.yaml` для платформ (linkedin, facebook тощо) у `known_accounts` можна вказати `email` та `profile_url` з цього профілю.
- `profile_identifiers.yaml` — єдине джерело істини для ідентифікаторів у privacy-аудиті; при зміні cv_pack_exporter.py оновлюйте і цей YAML.

## Запуск експорту CV-паку

З кореня репо:

```bash
python3 agent_core/data/cv_pack_exporter.py
```

Вихід: `agent_core/data/output_cv_pack/` (відносно скрипта).
