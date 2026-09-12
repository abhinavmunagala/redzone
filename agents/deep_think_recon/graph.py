from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_groq import ChatGroq

# No tools for deep think — pure reasoning
# It receives data and reasons, no tool calls

def build_graph(llm):
    """
    Deep Think uses a simple single-pass graph.
    No tool calls — pure LLM reasoning over recon data.
    """
    def reason_node(state: MessagesState):
        response = llm.invoke(state["messages"])
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("reason", reason_node)
    graph.add_edge(START, "reason")
    # no tool loop — single pass reasoning
    graph.add_edge("reason", "__end__")
    return graph.compile()