from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, BaseMessage
from app.llm.llm import llm
from app.llm.llm_manager import LLMOptions
from app.config import settings
from typing_extensions import Annotated, TypedDict
from typing import Sequence
from langgraph.graph.message import add_messages

# Define system prompt template
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a League of Legends assistant. Given a match with information about the players in the game, "
                "be concise and informative in your responses. "
                "Respond in a beautifully formatted Markdown. Use line separators or empty lines to separate "
                "logical sections. "
                "Do not provide information unrelated to the question."
            ),
        ),
        MessagesPlaceholder(variable_name="messages"),
        (
            "user",
            "Here is additional context about the match: {match}. Advise me based on the specific game.",
        ),
    ]
)

# Define chatbot workflow state
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    match: dict
    modelName: str

workflow = StateGraph(state_schema=State)

# Function to pick the appropriate model using the singleton
def pick_model(state: dict):
    try:
        if state["modelName"] == "gemini-1.5-flash":
            model = llm.get(LLMOptions.GEMINI_FLASH)
        else:
            model = llm.get(LLMOptions.GPT_MINI)
        return model
    except Exception as e:
        raise ValueError(f"Error in pick_model: {e}")

# Function to invoke the model
def call_model(state: dict):
    print(state)
    try:
        model = pick_model(state)  # Use the singleton to get the model
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

# Add model processing to the workflow
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Initialize in-memory message history
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Function to handle chatbot requests
def handle_chatbot_request(thread_id: str, query: str, match: dict = None, modelName="gemini-1.5-flash"):
    try:
        config = {"configurable": {"thread_id": thread_id}}
        input_messages = [HumanMessage(content=query)]
        state = {"messages": input_messages, "match": match, "modelName": modelName}
        return app.stream(state, config, stream_mode=["messages"])
    except Exception as e:
        print(f"Error in handle_chatbot_request: {e}")
        return "An error occurred while processing your request. Please try again later."
