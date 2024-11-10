from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

app = Flask(__name__)
CORS(app)

# Settings environment variables and API keys
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "default"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

# Initialize the search tool and LLM
search = TavilySearchResults(max_results=2)
tools = [search]
llm = ChatOpenAI(model="gpt-4o", temperature=0) # use either gpt-3.5-turbo or gpt-4o
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an agent that when given a location and a bunch of \
            different recycling goods, you will find the closest recycling \
            station based on that location and then give the user a price \
            estimate (give a final value) of how much they can make from the \
            recycling. Moreover, the user will give you their car type. \
            Figure out how much gas/electricity, by searching for the distance \
            and gas mileage (from the region where the user is from) it takes and subtract that from the total amount \
            they can make. You have access to the tavily api to search the web, make sure to crosscheck your sources for the prices! \
            After the calculations, can you write the answer after your logic in 1 line as such: \
            'The closest recycling plant is [location]. The amount you will make is [amount]'",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

@app.route('/query', methods=['POST'])
def run_query():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    location = data.get("location")
    recycling_amount = data.get("recycling_amount")
    car_make_model = data.get("car_make_model")
    query = f"Location: {location}, Recycling Amount: {recycling_amount}, Car: {car_make_model}"

    response = agent_executor({"input": query})
    output_text = response.get('output', 'No result available')

    return jsonify({
        "location": location,
        "amount": output_text
    })

# Endpoint to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    # Collect form data
    name = request.form.get('name')
    location = request.form.get('location')
    recyclables = request.form.get('recyclables')
    make = request.form.get('make')

    # Create a dictionary to store data
    form_data = {
        "name": name,
        "location": location,
        "recyclables": recyclables,
        "make": make
    }

    print(form_data)
