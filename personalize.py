# Персоналізація спілкування з хазяїном (host) та іншими.

from typing import Optional


def display_name(first_name: Optional[str], is_host: bool) -> str:
    """Имя для обращения: хозяин — по имени или «хозяин», остальные — по имени или «ты»."""
    name = (first_name or "").strip()
    if is_host:
        return (name or "хозяин") + (" (господар)" if name else "")
    return name or "ты"


def personalize(text: str, name: str, is_host: bool) -> str:
    """
    Персонализирует текст: для хозяина добавляет обращение по имени.
    «Ква.» -> «Ква, Ваня.» в начале; в конце можно «Держись, Ваня. Ква.»
    """
    disp_name = display_name(name, is_host)
    if not name or name in ("ты", "хозяин"):
        return text.replace("{name}", disp_name)
    result = text.replace("{name}", disp_name)
    if result.strip().startswith("Ква"):
        result = result.replace("Ква. ", f"Ква, {name}. ", 1)
        if result.startswith("Ква,"):
            pass
        elif result.strip().startswith("Ква "):
            result = f"Ква, {name}. " + result.strip()[3:].lstrip()
    if is_host and result.rstrip().endswith("Ква.") and name != "хозяин":
        result = result.rstrip()[:-4].rstrip() + f"\nДержись, {name}. Ква."
    return result
