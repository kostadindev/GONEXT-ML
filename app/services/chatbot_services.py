from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from app.config import settings

# Initialize ChatOpenAI model
model = ChatOpenAI(model="gpt-4o-mini", api_key=settings.openai_api_key)

# Define a system prompt
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a League of Legends assistant. Answer all questions to the best of your ability." +
            "You can respond with markdown to format responses beautifully where appropriate",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# Define chatbot workflow
workflow = StateGraph(state_schema=MessagesState)


def call_model(state: dict):
    # Use 'state["messages"]' instead of 'state.messages'
    prompt = prompt_template.invoke({"messages": state["messages"]})
    response = model.invoke(prompt)
    return {"messages": response}


workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Add in-memory message history
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Function to handle chatbot requests
def handle_chatbot_request(thread_id: str, query: str):
    config = {"configurable": {"thread_id": thread_id}}
    input_messages = [HumanMessage(content=query)]
    # Pass 'messages' as a dictionary
    output = app.invoke({"messages": input_messages}, config)
    return output["messages"][-1].content
