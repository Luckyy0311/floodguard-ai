import json

from .config import MAX_TOOL_CALLS
from .llm import llm_json
from .prompts import SYSTEM_PROMPT
from .rag import SimpleVectorStore
from .tools import (
    geocode_location,
    get_weather_risk,
    get_official_alerts,
    get_emergency_contacts
)


class FloodAgent:
    """
    Agentic flood risk assistant.
    """

    def __init__(self):
        self.store = SimpleVectorStore()
        self.store.load_or_build()
        self.trace = []

    def call_tool(self, tool_name, args):
        if not isinstance(args, dict):
            args = {}

        try:
            if tool_name == "geocode_location":
                return geocode_location(
                    args.get("query") or args.get("location")
                )

            if tool_name == "get_weather_risk":
                return get_weather_risk(
                    args.get("latitude"),
                    args.get("longitude")
                )

            if tool_name == "get_official_alerts":
                return get_official_alerts(
                    args.get("latitude"),
                    args.get("longitude")
                )

            if tool_name == "search_preparedness_docs":
                query = args.get("query") or args.get("topic")
                k = int(args.get("k", 3) or 3)

                return {
                    "results": self.store.search(query, k=k)
                }

            if tool_name == "get_emergency_contacts":
                return get_emergency_contacts(
                    args.get("location")
                )

            return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"error": str(e)}

    def run(self, user_message, default_location=None):
        self.trace = []

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        if default_location:
            messages.append({
                "role": "system",
                "content": (
                    "Default user location: "
                    f"{default_location}. "
                    "If the user does not explicitly provide a location, "
                    "use this default location for geocoding."
                )
            })

        messages.append({
            "role": "user",
            "content": user_message
        })

        for step in range(MAX_TOOL_CALLS):
            try:
                payload = llm_json(messages)
            except Exception as e:
                return {
                    "answer": f"LLM error: {str(e)}",
                    "risk_level": "unknown",
                    "trace": self.trace
                }

            if not isinstance(payload, dict):
                payload = {"answer": str(payload)}

            if payload.get("tool"):
                tool_name = payload.get("tool")
                tool_args = payload.get("args") or payload.get("arguments") or {}

                result = self.call_tool(tool_name, tool_args)

                self.trace.append({
                    "step": step + 1,
                    "tool": tool_name,
                    "args": tool_args,
                    "result": result
                })

                messages.append({
                    "role": "assistant",
                    "content": json.dumps({
                        "tool": tool_name,
                        "args": tool_args
                    })
                })

                messages.append({
                    "role": "user",
                    "content": (
                        f"TOOL RESULT for {tool_name}:\n"
                        f"{json.dumps(result, ensure_ascii=False)[:8000]}"
                    )
                })

                continue

            if payload.get("answer") is not None:
                if not isinstance(payload["answer"], str):
                    payload["answer"] = json.dumps(
                        payload["answer"],
                        ensure_ascii=False
                    )

                payload["trace"] = self.trace
                return payload

            return {
                "answer": json.dumps(payload, ensure_ascii=False),
                "risk_level": "unknown",
                "trace": self.trace
            }

        return {
            "answer": "I reached the maximum number of reasoning steps. Please try a simpler request.",
            "risk_level": "unknown",
            "trace": self.trace
        }