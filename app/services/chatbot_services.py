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

# Define system prompt template with language support
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a League of Legends assistant. Given a match with information about the players in the game, "
                "be concise and informative in your responses. Respond in beautifully formatted Markdown. "
                "Use line separators or empty lines to separate logical sections. "
                "Respond in the language specified: {language}."
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

# Define chatbot workflow state with language support
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    match: dict
    modelName: str
    language: str  # New field to specify the response language

workflow = StateGraph(state_schema=State)


# Function to invoke the model with language handling
def call_model(state: dict):
    try:
        model = llm.get(state["modelName"])  # Use the singleton to get the model
        match = state.get("match", {})
        language = state.get("language", "English")  # Default to English if not provided
        prompt = prompt_template.invoke({
            "messages": state["messages"],
            "match": match,
            "language": language,
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

# Function to handle chatbot requests with language support
def handle_chatbot_request(thread_id: str, query: str, match: dict = None, modelName="gemini-1.5-flash", language="English"):
    try:
        config = {"configurable": {"thread_id": thread_id}}
        input_messages = [HumanMessage(content=query)]
        print("language: ", language)
        state = {"messages": input_messages, "match": match, "modelName": modelName, "language": language}
        return app.stream(state, config, stream_mode=["messages"])
    except Exception as e:
        print(f"Error in handle_chatbot_request: {e}")
        return "An error occurred while processing your request. Please try again later."
