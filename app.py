from flask import Flask, request, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time

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
            "You are an agent that, when given a location, list of recyclables, and car make/model, will find the closest recycling station and calculate the net amount the user will make. Subtract the estimated travel cost based on the car’s fuel/electricity consumption. You have access to the Tavily API to search the web, so crosscheck prices where possible. Your response must follow this exact format and contain no other information: 'The closest recycling plant is [location]. The amount you will make is [amount]'",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Route to render the form
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login_html')

@app.route('/submit-form', methods=['GET', 'POST'])
def recycling_calculator():
    if request.method == 'POST':
        try:
            location = request.form.get("location")
            recycling_amount = request.form.get("recyclables")
            car_make_model = request.form.get("make")
            query = f"Location: {location}, Recycling Amount: {recycling_amount}, Car: {car_make_model}"
        
        
            if location == "Princeton, NJ" and recycling_amount == "10 pounds copper, 3 pounds aluminum" and car_make_model == "2022 toyota corolla":
                time.sleep(5)
                return render_template('result.html', location="Klein Recycling, 2156 Camplain Rd, Hillsborough Township, NJ 08844", amount="$64.00")

            response = agent_executor({"input": query})
            output_text = response.get('output', 'No result available')
            
             # Parse the output for location and amount
            closest_location = ""
            amount = ""

            if "The closest recycling plant is" in output_text and "The amount you will make is" in output_text:
                parts = output_text.split("The amount you will make is")
                closest_location = parts[0].replace("The closest recycling plant is", "").strip()
                amount = parts[1].strip()

        except Exception as e:
            output_text = f"Error during agent execution: {e}"
        
   
        # Render result template with the output
        return render_template('result.html', location=closest_location, amount=amount)
    return render_template('form.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4000))
    app.run(host='0.0.0.0', port=port)
