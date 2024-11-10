from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from database import retrieve_response_from_databricks, save_response_to_databricks


app = Flask(__name__)

# Settings environment variables and API keys
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "default"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

# Initialize LangChain components (replace with your tools and prompt as needed)
search = TavilySearchResults(max_results=2)
tools = [search]
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
agent = create_tool_calling_agent(llm, tools)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Process the query, check the database first, and generate a response if needed
def process_query(query):
    # Check for an existing response in the database
    existing_responses = retrieve_response_from_databricks(query)
    
    if existing_responses:
        print("Response retrieved from database.")
        return existing_responses[0]["response"]

    # Generate a new response if not found in the database
    response_text = ""
    for chunk in agent_executor.stream({"input": query}):
        response_text += str(chunk)
    
    # Save the new response to the database
    save_response_to_databricks(query, response_text)
    print("New response saved to database.")
    return response_text


@app.route('/query', methods=['POST'])
def query():
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    response_text = process_query(query)
    return jsonify({"response": response_text}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
