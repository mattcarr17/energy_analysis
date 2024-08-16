import os
import ast
import pandas as pd
from openai import OpenAI
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import gradio as gr

load_dotenv()

# Create LLM Client
client = OpenAI(api_key=os.getenv("API_KEY"))

# Import data
data = pd.read_csv('./app_data/data.csv')

data_dictionary = """
Data Dictionary:
* YEAR: Year of the data
* NAMEPCAP: Total U.S. capacity
* USNGENAN: Total Generation/Electricity Generated
* USCO2AN: Total CO2 Emissions
* USCO2EQA: Total CO2 Equivalent Emissions
* USCO2RTA: CO2 Emission Rate
* USC2ERTA: CO2 Equivalent Emission Rate
"""

def create_response(query):

    prompt = f"""

    You are an AI assistant specializing in data analysis and visualization around the energy system. You have access to 
    a dataset with U.S. energy statistics in the following format:

    {data_dictionary}

    As an assistant, it is your job to support experts in their exploration and research on the energy system. We want this research
    to be data-centric whenever possible. You will answer questions about the energy system and will reference the provided data whenever
    relevant. 

    For each query, you will do the following:
    - Determine the question being asked can be answered using the data you have access to, if the data can support your answer, or, if the data is irrelevant for question
    - If data can answer the question:
        - Create a visualization using the Plotly library from Python to answer the question
        - Explain the visual and how the data being presented clearly answers the users questions
        - Provide an interpretation. Reference key statistics in your written answer
    - If data can support your answer
        - Provide a text response answering the question to the best of your knowledge
        - Create a visualization using the Plotly library from and the data at your disposal to support claims in your written answer
        - Reference the visualization in your written response, including any key statistics
    - If data cannot answer or support your answer (ie. is irrelevant to your response)
        - Answer the question to the best of your ability (this includes saying you do not know the answer)
        - Since the data cannot support your answer, we do not need to create a visualization on the provided data itself,
            using the Plotly library from Python, create a simple, fun/funny visual to display (eg. smiley face)

    Given the following question: "{query}"

    1. Check the data to determine if it can be used to answer the question
    2. Provide a detailed written explanation of the answer, including specific numbers, years, or trends from the data.
    3. Decide if a visualization would be helpful to support your explanation/answer
    4. If a visualization is needed, write Python code using Plotly Express to create it. The data is stored in a pandas dataframe, "data"
    5. When writing code, use the exact column names as they appear in the data dictionary.
    6. Format your response as follows:
        ANSWER: [Detailed, data-driven answer here including specific statistics from the data]
        VISUALIZATION:
        ```python
        [Python code here for visualization]
        ```
    """

    response = client.chat.completions.create(
        model = 'gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are a helpful assistant skilled in data analysis and research. You provide data-driven asnwers whenever possible. You respond in a professional manner, but keep it light and humerous when the opportunity presents itself"},
            {"role": "user", "content": prompt}
        ])
    
    return response.choices[0].message.content


def execute_visualization(code):

    local_vars = {"data": data, "px": px, "go": go}
    exec(code, globals(), local_vars)
    return local_vars.get("fig")


def process_question(question):

    response = create_response(question)

    # Parse explanation and code
    explanation = response.split("ANSWER:")[1].split("VISUALIZATION:")[0].strip()
    code = response.split('VISUALIZATION:')[1].split('```python')[1].split('```')[0].strip()

    # Execute visualization
    visualization = execute_visualization(code)

    return explanation, visualization


def respond(question):
    """Interface function between Gradio frontend and RAG backend."""

    explanation, visual = process_question(question)
    # Test?
    return explanation, visual

gradio_interface = gr.Interface(
    fn = respond,
    inputs=[gr.Textbox(label='Enter question about U.S. Energy System')],
    outputs = [gr.Textbox(), gr.Plot()],
    title='U.S. Energy Data Q&A System'
)

gradio_interface.launch()