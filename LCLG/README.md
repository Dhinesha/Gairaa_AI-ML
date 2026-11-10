# LangGraph and LangChain Gemini Chatbot

This is a basic implementation of a conversational agent using LangChain, LangGraph, and Google's Gemini LLM.

## How it works

1. **LangChain** provides the LLM wrapper (`ChatGoogleGenerativeAI`) which standardizes how we communicate with the Gemini API.
2. **LangGraph** provides the structure for the agent. It works like a state machine:
   - **State**: We define a `State` object (in our case, just a list of `messages`).
   - **Nodes**: We define Python functions (like `chatbot()`) that take the current State, do some processing (e.g., call the LLM), and return an updated State.
   - **Edges**: We connect the nodes together to form a graph (`START` -> `chatbot` -> `END`).
3. When the user inputs a message, it gets added to the State, passed to the `chatbot` node, the LLM generates a response, the response is appended to the State, and the loop repeats.

## Setup Instructions

1. Ensure you have Python installed.
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to a new file named `.env`:
   ```bash
   copy .env.example .env
   ```
5. Get a Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey) and paste it into your `.env` file.

## Running the Application

```bash
python main.py
```
