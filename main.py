import os
from dotenv import load_dotenv

from typing import Literal

from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver

from langchain_openai import ChatOpenAI

from tools import get_current_stock_price, get_stock_price, get_trend, show_graph, show_multiline_graph

load_dotenv()

tools = [get_current_stock_price, get_stock_price, get_trend, show_graph, show_multiline_graph]
llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY")
).bind_tools(tools)

def expert(state: MessagesState):
    system_message = """Analyze stock data to identify and explain trends to users.

You must evaluate the given stock data, identify significant trends, and describe these trends in a clear and insightful manner to the user.

# Steps

1. **Data Analysis**: Examine the stock data over a specified period. Look for patterns such as rising, falling, or stable trends.
2. **Trend Identification**: Identify key trends in the stock data. Consider factors like price changes, trading volume, and any other relevant indicators.
3. **Explanation**: Provide a clear and concise explanation of the identified trends. Ensure the explanation is user-friendly and informative.
4. **Additional Insights**: If applicable, offer insights into potential causes for the trends, such as market events, economic indicators, or sector performance.

# Output Format

- A well-structured paragraph or two summarizing the analysis and key trends.
- Include specific data points to support your explanations (e.g., percentage changes, dates, volumes).
- Call show_graph tool when 'show', 'plot' or something similar is told by the user.

# Notes

- Ensure that the analysis is accessible and understandable to users without a deep financial background.
- Always base explanations on the provided data and avoid assumptions not supported by the data.
- Consider edge cases where data might be incomplete or inconsistent and ask the user for the proper data.
- Represent the period parameter of get_trend in the following manner
Ex- 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
- Do not directly give the tool output
- Do not just show the trend percentage, describe it as well (+ve is upward trend, -ve is downward trend)
- If the tool returns an error message, RETURN THE ERROR MESSAGE, DO NOT TRY TO CALL THE TOOL AGAIN
- Directly pass get_stock_price into y_values of show_graph if they ask for graph
- Put the date as the x-axis properly, the current date is 3/16
"""

    messages = state["messages"]
    response = llm.invoke([system_message] + messages)

    return {"messages": [response]}

tool_node = ToolNode(tools)

def should_continue(state: MessagesState) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tools"

    return END

graph = StateGraph(MessagesState)

graph.add_node("expert", expert)
graph.add_node("tools", tool_node)

graph.add_edge(START, "expert")
graph.add_conditional_edges("expert", should_continue)
graph.add_edge("tools", "expert")
graph.add_edge("expert", END)

checkpointer = MemorySaver()

app = graph.compile(checkpointer=checkpointer)

while True:
    user_input = input(">> ")
    if user_input.lower() in ["quit", "exit"]:
        print("Exiting...")
        break

    response = app.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config={"configurable": {"thread_id": 1}}
    )

    print(response["messages"][-1].content)