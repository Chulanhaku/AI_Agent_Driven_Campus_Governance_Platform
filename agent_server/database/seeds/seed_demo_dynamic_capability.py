from app.db.models import DynamicPlanDefinition, DynamicToolDefinition
from app.db.session import SessionLocal


def seed_demo_dynamic_capability() -> None:
    db = SessionLocal()
    try:
        exists = db.query(DynamicToolDefinition).filter(
            DynamicToolDefinition.tool_name == "query_demo_course_catalog"
        ).first()
        if exists:
            print("demo dynamic capability already exists")
            return

        tool_def = DynamicToolDefinition(
            source_proposal_id=None,
            tool_name="query_demo_course_catalog",
            primary_intent="dynamic_course_catalog_query",
            tool_type="db_query",
            description="动态查询课程目录",
            input_schema_json={
                "keyword": "string|null",
            },
            execution_config_json={
                "table_name": "courses",
                "allowed_columns": ["course_code", "course_name", "semester", "course_type"],
                "keyword_param": "keyword",
                "default_limit": 5,
            },
            status="active",
        )
        db.add(tool_def)
        db.flush()

        plan_def = DynamicPlanDefinition(
            source_proposal_id=None,
            capability_name="dynamic_course_catalog_query",
            primary_intent="dynamic_course_catalog_query",
            description="动态课程目录查询",
            plan_json={
                "primary_intent": "dynamic_course_catalog_query",
                "steps": [
                    {
                        "type": "call_dynamic_tool",
                        "tool_name": "query_demo_course_catalog",
                        "params_template": {
                            "keyword": "$slot.keyword",
                        },
                    },
                    {
                        "type": "compose_dynamic",
                    },
                ],
            },
            status="active",
        )
        db.add(plan_def)

        db.commit()
        print("seed demo dynamic capability success")
    except Exception as exc:
        db.rollback()
        print(f"seed demo dynamic capability failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_dynamic_capability()