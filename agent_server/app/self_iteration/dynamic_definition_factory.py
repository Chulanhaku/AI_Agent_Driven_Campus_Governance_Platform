class DynamicDefinitionFactory:
    def build_from_tool_spec_proposal(
        self,
        *,
        proposal_id: int,
        proposal: dict,
    ) -> dict:
        proposal_type = proposal.get("proposal_type")
        if proposal_type != "tool_spec":
            raise ValueError("Only tool_spec proposal can be converted to dynamic definitions")

        capability_name = proposal.get("capability_name")
        if not capability_name:
            raise ValueError("tool_spec proposal missing capability_name")

        tool_spec = proposal.get("tool_spec") or {}
        tool_name = tool_spec.get("name") or capability_name
        description = tool_spec.get("description") or proposal.get("reason") or capability_name
        inputs = tool_spec.get("inputs") or {}
        data_sources = tool_spec.get("data_sources") or []
        read_only = bool(tool_spec.get("read_only", True))

        # 第一版先只支持 db_query / web_search 两类动态工具
        dynamic_tool_type = self._infer_dynamic_tool_type(
            tool_spec=tool_spec,
            data_sources=data_sources,
        )

        execution_config_json = self._build_execution_config(
            tool_type=dynamic_tool_type,
            proposal=proposal,
            tool_spec=tool_spec,
        )

        planner_patch = proposal.get("planner_patch")
        if planner_patch and isinstance(planner_patch, dict):
            primary_intent = planner_patch.get("primary_intent") or capability_name
            plan_json = planner_patch
        else:
            primary_intent = capability_name
            plan_json = {
                "primary_intent": primary_intent,
                "steps": [
                    {
                        "type": "call_dynamic_tool",
                        "tool_name": tool_name,
                        "params_template": self._build_default_params_template(inputs),
                    },
                    {
                        "type": "compose_dynamic",
                    },
                ],
            }

        return {
            "dynamic_tool_definition": {
                "source_proposal_id": proposal_id,
                "tool_name": tool_name,
                "primary_intent": primary_intent,
                "tool_type": dynamic_tool_type,
                "description": description,
                "input_schema_json": inputs,
                "execution_config_json": execution_config_json,
                "status": "active",
            },
            "dynamic_plan_definition": {
                "source_proposal_id": proposal_id,
                "capability_name": capability_name,
                "primary_intent": primary_intent,
                "description": description,
                "plan_json": plan_json,
                "status": "active",
            },
        }

    def _infer_dynamic_tool_type(
        self,
        *,
        tool_spec: dict,
        data_sources: list,
    ) -> str:
        execution_mode = tool_spec.get("execution_mode")
        if execution_mode in {"db_query", "web_search"}:
            return execution_mode

        if "db_search" in data_sources or "database" in data_sources:
            return "db_query"

        if "web_research" in data_sources or "web_search" in data_sources:
            return "web_search"

        return "db_query"

    def _build_execution_config(
        self,
        *,
        tool_type: str,
        proposal: dict,
        tool_spec: dict,
    ) -> dict:
        raw_config = tool_spec.get("execution_config") or {}

        if tool_type == "db_query":
            return {
                "table_name": raw_config.get("table_name"),
                "allowed_columns": raw_config.get("allowed_columns", []),
                "keyword_param": raw_config.get("keyword_param", "keyword"),
                "default_limit": raw_config.get("default_limit", 10),
                "exact_filters": raw_config.get("exact_filters", {}),
            }

        if tool_type == "web_search":
            return {
                "query_param": raw_config.get("query_param", "keyword"),
                "max_results": raw_config.get("max_results", 5),
            }

        return raw_config

    def _build_default_params_template(
        self,
        inputs: dict,
    ) -> dict:
        params_template = {}
        for key in inputs.keys():
            params_template[key] = f"$slot.{key}"
        return params_template