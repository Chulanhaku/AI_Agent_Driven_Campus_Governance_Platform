from pathlib import Path


class ToolSpecCodegen:
    def __init__(self, output_dir: str = "generated_tools") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_stub(
        self,
        *,
        proposal_id: int,
        proposal: dict,
    ) -> dict:
        tool_spec = proposal.get("tool_spec", {}) or {}
        tool_name = tool_spec.get("name") or proposal.get("capability_name") or f"generated_tool_{proposal_id}"
        capability_name = proposal.get("capability_name") or tool_name

        class_name = "".join(part.capitalize() for part in tool_name.split("_")) + "Tool"
        file_name = f"{tool_name}.py"
        file_path = self.output_dir / file_name

        description = tool_spec.get("description", "Generated tool stub")
        inputs = tool_spec.get("inputs", {})

        code_text = f'''from app.tools.base import BaseTool


class {class_name}(BaseTool):
    name = "{tool_name}"
    description = "{description}"

    def run(self, **kwargs) -> dict:
        return {{
            "success": False,
            "message": "generated tool stub not implemented yet",
            "expected_inputs": {inputs},
        }}
'''

        file_path.write_text(code_text, encoding="utf-8")

        return {
            "capability_name": capability_name,
            "tool_name": tool_name,
            "file_path": str(file_path),
            "artifact_type": "tool_stub",
            "code_text": code_text,
            "content_json": tool_spec,
        }