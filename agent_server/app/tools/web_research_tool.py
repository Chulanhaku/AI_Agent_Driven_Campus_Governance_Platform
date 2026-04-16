import requests

from app.config.settings import get_settings
from app.tools.base import BaseTool
from app.self_iteration.research_rules import ResearchRules


class WebResearchTool(BaseTool):
    name = "web_research"
    description = "执行受控网页搜索，仅返回搜索摘要结果"

    def run(
        self,
        *,
        query: str,
        max_results: int = 5,
        **kwargs,
    ) -> dict:
        settings = get_settings()

        if not settings.self_iteration_enable_web_research:
            return {
                "success": True,
                "results": [],
                "message": "web research disabled",
            }

        if not settings.serper_api_key:
            return {
                "success": True,
                "results": [],
                "message": "serper api key not configured",
            }

        allowed_domains = ResearchRules.get_allowed_domains()
        final_query = query
        if allowed_domains:
            domain_part = " OR ".join([f"site:{domain}" for domain in allowed_domains])
            final_query = f"{query} ({domain_part})"

        headers = {
            "X-API-KEY": settings.serper_api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "q": final_query,
            "num": max_results,
        }

        response = requests.post(
            settings.serper_search_url,
            headers=headers,
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()

        organic = data.get("organic", []) or []
        results = []
        for item in organic[:max_results]:
            results.append(
                {
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                }
            )

        return {
            "success": True,
            "query": final_query,
            "results": results,
        }