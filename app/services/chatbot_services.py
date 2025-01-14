from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from app.config import settings
import json
from typing_extensions import Annotated, TypedDict
from typing import Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


# Initialize ChatOpenAI model
model = ChatOpenAI(model="gpt-4o", api_key=settings.openai_api_key)

# Define a system prompt
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a League of Legends assistant. Given a match with information about the players in the game, " +
            "Be concise and informative in your responses. " +
            "Respond in a beautifully formatted Markdown. Use line separators or empty lines to separate "+
            "logical sections" +
            "Do not provide information unrelated to the question. "
        ),
        MessagesPlaceholder(variable_name="messages"),
        (
            "user",
            "Here is additional context about the match: {match}. Advise me based on the specific game",
        ),
    ]
)

# Define chatbot workflow

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    match: dict


workflow = StateGraph(state_schema=State)


def call_model(state: dict):
    try:
        match = state.get("match", {})
        prompt = prompt_template.invoke({
            "messages": state["messages"],
            "match": match,
        })
        response = model.invoke(prompt)
        return {"messages": response}
    except Exception as e:
        print(f"Error in call_model: {e}")
        return {"messages": ["Error occurred while processing the model."]}


workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Add in-memory message history
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Function to handle chatbot requests
def handle_chatbot_request(thread_id: str, query: str, match: dict = None):
    # print("Received match:", match)
    try:
        config = {"configurable": {"thread_id": thread_id}}
        input_messages = [HumanMessage(content=query)]
        state = {"messages": input_messages, "match": match}
        output = app.invoke(state, config)
        print(output["messages"][-1].content)
        return output["messages"][-1].content
    except Exception as e:
        print(f"Error in handle_chatbot_request: {e}")
        return "An error occurred while processing your request. Please try again later."

