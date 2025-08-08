"""
Script Name: model.py
Author: Deniz
Created: 2024-08-24 19:53:43
Description: Script Description
"""

from langchain import PromptTemplate
from langchain.llms import HuggingFaceEndpoint

hugging_face_token = "YOUR HUGGING FACE TOKEN"

# Define the prompt template
template = "You are an artificial intelligence assistant, answer the question: {question}"
prompt = PromptTemplate(template=template, input_variables=["question"])

# Create a HuggingFace LLM instance
llm = HuggingFaceEndpoint(repo_id='tiiuae/falcon-7b-instruct', huggingfacehub_api_token=hugging_face_token)

# Create a function to process the question and get the response
def get_response(question):
    # Format the prompt with the question
    formatted_prompt = prompt.format(question=question)
    # Generate the response using the LLM
    response = llm.invoke(formatted_prompt)
    return response
