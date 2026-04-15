class IntentCatalog:
    STATIC_PRIMARY_INTENTS = [
        "query_schedule",
        "campus_card_topup",
        "leave_create",
        "policy_qa",
        "course_plan_generate",
        "course_plan_submit",
        "resource_booking_generate",
        "resource_booking_submit",
        "zero_form_approval_generate",
        "zero_form_approval_submit",
        "fallback",
    ]

    STATIC_SECONDARY_INTENTS = [
        "time_planning_advice",
        "weekly_busyness_analysis",
    ]

    @classmethod
    def get_static_primary_intents(cls) -> list[str]:
        return list(cls.STATIC_PRIMARY_INTENTS)

    @classmethod
    def get_static_secondary_intents(cls) -> list[str]:
        return list(cls.STATIC_SECONDARY_INTENTS)

    @classmethod
    def merge_primary_intents(
        cls,
        *,
        dynamic_primary_intents: list[str] | None = None,
    ) -> list[str]:
        merged = list(cls.STATIC_PRIMARY_INTENTS)
        if dynamic_primary_intents:
            for item in dynamic_primary_intents:
                if item not in merged:
                    merged.append(item)
        return merged