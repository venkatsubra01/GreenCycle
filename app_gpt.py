from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

app = Flask(__name__)

# Settings environment variables and API keys
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "default"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TAVILY_SEARCH_KEY"] = os.getenv("TAVILY_SEARCH_KEY")

# Initialize the search tool and LLM
search = TavilySearchResults(max_results=8)
tools = [search]
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0) # use either gpt-3.5-turbo or gpt-4o
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an agent that when given a location and a bunch of different recycling goods, you will find the closest recycling station based on that location and then give the user a price estimate of how much they can make from the recycling. Moreover, the user will give you their car type. Figure out how much gas/electricity it takes and subtract that from the total amount they can make. You have access to the tavily api to search the web! ",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

@app.route('/query', methods=['POST'])
def run_query():
    try:
        data = request.json
        if data is None:
            print("No JSON data received")  # Clearer debugging
            return jsonify({"error": "No JSON data received"}), 400
        print("Received data:", data)  # This should show the incoming payload

        user_query = data.get('query')
        if not user_query:
            return jsonify({"error": "No query provided"}), 400

        response_chunks = []
        for chunk in agent_executor.stream({"input": user_query}):
            chunk = str(chunk)
            chunk_length = len(chunk)
            segment_size = 100  # Adjust the segment size as needed

            for i in range(0, chunk_length, segment_size):
                response_chunks.append(chunk[i:i+segment_size])
    except Exception as e:
        response_chunks = str(e)
    
    return jsonify({"response": response_chunks})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)