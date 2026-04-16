from app.config.settings import get_settings


class ResearchRules:
    @staticmethod
    def get_allowed_domains() -> list[str]:
        settings = get_settings()
        raw = settings.self_iteration_allowed_domains.strip()
        if not raw:
            return []
        return [item.strip() for item in raw.split(",") if item.strip()]

    @staticmethod
    def get_allowlist_tables() -> list[str]:
        settings = get_settings()
        raw = settings.self_iteration_db_allowlist_tables.strip()
        return [item.strip() for item in raw.split(",") if item.strip()]

    @staticmethod
    def is_table_allowed(table_name: str) -> bool:
        return table_name in set(ResearchRules.get_allowlist_tables())