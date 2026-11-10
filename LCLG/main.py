import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
load_dotenv()
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
def chatbot(state: State):
    response = llm.invoke(state["messages"])

    return {"messages": [response]}
def build_graph():
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_edge(START, "chatbot")

    graph_builder.add_edge("chatbot", END)
    graph = graph_builder.compile()
    
    return graph
def main():
    if not os.environ.get("GOOGLE_API_KEY"):
        print("---------------------------------------------------------")
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        print("Please copy '.env.example' to '.env' and add your key.")
        print("Get an API key here: https://aistudio.google.com/app/apikey")
        print("---------------------------------------------------------")
        return

    graph = build_graph()
    
    print("\n========================================================")
    print("Welcome to the LangGraph + Gemini Chatbot!")
    print("Type 'quit' or 'exit' to end the conversation.")
    print("========================================================\n")
    
    chat_history = []
    
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            chat_history.append(HumanMessage(content=user_input))
            events = graph.stream(
                {"messages": chat_history}, 
                stream_mode="values" 
            )
            
            for event in events:
                last_message = event["messages"][-1]
                if last_message.type == "ai":
                    content = last_message.content
                    if isinstance(content, list):
                        content = " ".join(
                            part["text"] for part in content
                            if isinstance(part, dict) and part.get("type") == "text"
                        )
                    print(f"\nGemini: {content}\n")
                    chat_history.append(last_message)
                    
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    main()
