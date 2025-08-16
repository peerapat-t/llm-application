# graph.py
from typing import List, Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from agent import agent_runnables
from supervise import topic_check_chain, filter_chain, supervisor_chain

# --- Graph State Definition ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    next: str

# --- Graph Node Definitions ---
def topic_check_node(state: AgentState):
    print("---TOPIC CHECK: Analyzing query topic---")
    result = topic_check_chain.invoke({"messages": state["messages"]})
    if result.decision == "off_topic":
        print("---TOPIC CHECK: Detected off-topic question. Ending conversation.---")
        rejection_message = AIMessage(content="I can only assist with questions about our products. Please ask a relevant question.")
        return {"messages": [rejection_message], "next": "END"}
    print("---TOPIC CHECK: Query is on-topic. Proceeding to filter.---")
    return {"next": "filter"}

def filter_node(state: AgentState):
    print("---FILTER: Analyzing for multiple questions---")
    result = filter_chain.invoke({"messages": state["messages"]})
    if result.decision == "multi_question":
        print("---FILTER: Detected multiple questions. Ending conversation.---")
        rejection_message = AIMessage(content="I can only handle one question at a time. Please ask your questions separately.")
        return {"messages": [rejection_message], "next": "END"}
    print("---FILTER: Single question detected. Proceeding to supervisor.---")
    return {"next": "supervisor"}

def supervisor_node(state: AgentState):
    print("---SUPERVISOR: Deciding next action---")
    if not isinstance(state['messages'][-1], HumanMessage):
        return {"next": "END"}
    result = supervisor_chain.invoke({"messages": state["messages"]})
    if result.next == "FINISH":
        print("---SUPERVISOR: Conversation is finished.---")
        return {"next": "END"}
    print(f"---SUPERVISOR: Routing to {result.next}---")
    return {"next": result.next}

def agent_node(state: AgentState, agent_name: str):
    result = agent_runnables[agent_name].invoke(state)
    return {"messages": result["messages"]}

# --- Graph Construction ---
graph = StateGraph(AgentState)

graph.add_node("topic_checker", topic_check_node)
graph.add_node("filter", filter_node)
graph.add_node("supervisor", supervisor_node)
for agent_name in agent_runnables.keys():
    graph.add_node(agent_name, lambda state, name=agent_name: agent_node(state, name))

graph.set_entry_point("topic_checker")
graph.add_conditional_edges("topic_checker", lambda state: state["next"], {"filter": "filter", "END": END})
graph.add_conditional_edges("filter", lambda state: state["next"], {"supervisor": "supervisor", "END": END})
graph.add_conditional_edges("supervisor", lambda state: state["next"], {**{agent: agent for agent in agent_runnables.keys()}, "END": END})
for agent_name in agent_runnables.keys():
    graph.add_edge(agent_name, "supervisor")

# --- Compile the graph ---
app = graph.compile()
print("Graph compiled successfully!")