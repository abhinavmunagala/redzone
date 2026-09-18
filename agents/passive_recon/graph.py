from langgraph.graph import MessageGraph
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Any


def build_graph(llm: Any) -> MessageGraph:
    graph = MessageGraph()

    graph.add_node(
        "analyst",
        lambda state: [
            state["messages"][-1],
            HumanMessage(content=(
                "Analyze this reconnaissance data and provide "
                "structured intelligence assessment."
            ))
        ] + [
            SystemMessage(
                content="You are consolidating OSINT from "
                "multiple passive sources."
            )
        ]
    )

    graph.add_node(
        "analyzer",
        lambda state: [
            state["messages"][-1],
            HumanMessage(
                content="Provide final intelligence summary."
            )
        ]
    )

    graph.add_edge("analyst", "analyzer")
    graph.set_entry_point("analyst")
    graph.set_finish_point("analyzer")

    return graph.compile()
