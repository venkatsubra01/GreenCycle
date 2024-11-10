import os
from dotenv import load_dotenv
from databricks import sql
from datetime import datetime
import uuid

load_dotenv()

# Establish the Databricks SQL connection
connection = sql.connect(
    server_hostname=os.getenv("DATABRICKS_HOST"),
    http_path="/sql/1.0/endpoints/{YOUR_ENDPOINT_ID}",  # Replace with your endpoint ID
    access_token=os.getenv("DATABRICKS_TOKEN")
)

# Function to save response to Databricks
def save_response_to_databricks(query, response_text):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ai_responses.responses (id, query, response, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (str(uuid.uuid4()), query, response_text, datetime.now())
            )
        print("Response saved successfully to Databricks.")
    except Exception as e:
        print(f"Error saving response to Databricks: {e}")

# Function to retrieve responses from Databricks
def retrieve_response_from_databricks(query=None):
    try:
        with connection.cursor() as cursor:
            if query:
                cursor.execute(
                    """
                    SELECT * FROM ai_responses.responses
                    WHERE query = ?
                    LIMIT 1
                    """, (query,)
                )
            else:
                cursor.execute("SELECT * FROM ai_responses.responses")
            
            # Fetch all results
            results = cursor.fetchall()
            # Format results as a list of dictionaries
            responses = [
                {"id": row[0], "query": row[1], "response": row[2], "timestamp": row[3]}
                for row in results
            ]
            return responses
    except Exception as e:
        print(f"Error retrieving response from Databricks: {e}")
        return []
