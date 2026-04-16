class CapabilityPolicy:
    def decide(
        self,
        *,
        proposal: dict,
        validation_result: dict,
    ) -> dict:
        proposal_type = proposal.get("proposal_type")
        confidence_score = float(validation_result.get("confidence_score", 0.0))
        risk_level = validation_result.get("risk_level", "medium")

        if not validation_result.get("valid"):
            return {
                "final_status": "rejected",
                "activation_policy": "reject",
                "reason": validation_result.get("reason"),
            }

        if proposal_type == "tool_spec":
            return {
                "final_status": "validated",
                "activation_policy": "review_required",
                "reason": "tool_spec requires manual review",
            }

        if proposal_type == "knowledge_patch":
            if confidence_score >= 0.75 and risk_level == "low":
                return {
                    "final_status": "activated",
                    "activation_policy": "auto_activate",
                    "reason": "knowledge_patch low risk and high confidence",
                }
            return {
                "final_status": "validated",
                "activation_policy": "review_required",
                "reason": "knowledge_patch needs manual review",
            }

        if proposal_type == "plan_patch":
            if confidence_score >= 0.88 and risk_level in {"low", "medium"}:
                return {
                    "final_status": "activated",
                    "activation_policy": "auto_activate",
                    "reason": "plan_patch safe enough for auto activation",
                }
            return {
                "final_status": "validated",
                "activation_policy": "review_required",
                "reason": "plan_patch needs manual review",
            }

        return {
            "final_status": "validated",
            "activation_policy": "review_required",
            "reason": "default review_required",
        }